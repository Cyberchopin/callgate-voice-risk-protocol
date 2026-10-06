"""Start two ephemeral loopback processes. No cloud call or persistent key file.

Run: python -m scripts.start_review_demo
Only the reviewer child generates/holds its private key. Startup URLs are local
role capabilities; keep the reviewer URL away from the participant browser.
"""
import argparse
import json
import multiprocessing as mp
import os
import secrets
import socket
import time
from pathlib import Path
from urllib.request import Request, build_opener, HTTPRedirectHandler
from urllib.error import HTTPError

import uvicorn
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey, Ed25519PublicKey
from callgate.confirmation import ConfirmationCoordinator
from callgate.contacts import ContactDirectory, SavedContact
from callgate.review_transport import create_broker_app, create_reviewer_app
from callgate.verification import DemoVerificationGate
from callgate.workflow import DemoWorkflow


class NoRedirects(HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None


def _reviewer(public_pipe, broker_origin, reviewer_origin, reviewer_token, listener):
    key = Ed25519PrivateKey.generate()
    public_pipe.send_bytes(key.public_key().public_bytes(
        serialization.Encoding.Raw, serialization.PublicFormat.Raw))
    public_pipe.close()
    opener = build_opener(NoRedirects)

    def call(path, body=None):
        request = Request(broker_origin + path,
            data=None if body is None else json.dumps(body).encode(),
            headers={'Authorization': 'Bearer ' + reviewer_token, 'Content-Type': 'application/json'})
        try:
            with opener.open(request, timeout=5) as response:
                return json.load(response)
        except HTTPError as error:
            if error.code == 409:
                raise ValueError('confirmation no longer valid') from None
            raise

    app = create_reviewer_app(key, reviewer_token,
        lambda: call('/api/review/pending'),
        lambda submission: call('/api/review/decision', submission.model_dump()), origin=reviewer_origin,
        expected_reviewer='local-reviewer')
    uvicorn.Server(uvicorn.Config(app, access_log=False, log_level='warning')).run(sockets=[listener])


def _broker(public_bytes, participant_token, reviewer_token, origin, listener, contact_identity):
    issuer = Ed25519PrivateKey.generate()
    coordinator = ConfirmationCoordinator('local-demo', issuer,
        {'local-reviewer': Ed25519PublicKey.from_public_bytes(public_bytes)},
        contacts=ContactDirectory([SavedContact(identity=contact_identity, reviewer='local-reviewer',
            credential_origin='local-reviewer-process')]), initiator_origin='local-participant-session')
    workflow = DemoWorkflow(coordinator, DemoVerificationGate({'local-demo': issuer.public_key()}),
                            'local-reviewer')
    app = create_broker_app(workflow, participant_token, reviewer_token, origin=origin,
        reviewer_identity='local-reviewer',
        metrics_database=Path(__file__).resolve().parents[1] / 'callgate-metrics.sqlite3')
    uvicorn.Server(uvicorn.Config(app, access_log=False, log_level='warning')).run(sockets=[listener])


def _bind(port):
    sock = socket.socket()
    try:
        sock.bind(('127.0.0.1', port))
        sock.listen(128)
        return sock
    except BaseException:
        sock.close()
        raise


def _bind_with_fallback(preferred_port):
    for port in [preferred_port, 0]:
        try:
            return _bind(port)
        except OSError as error:
            if port == preferred_port and error.errno in {48, 98, 10048}:
                continue
            raise


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--participant-port', type=int, default=8766)
    parser.add_argument('--reviewer-port', type=int, default=8767)
    parser.add_argument('--contact-identity', default='saved-family',
        help='Synthetic saved identity provisioned before this disposable session')
    args = parser.parse_args()
    SavedContact(identity=args.contact_identity, reviewer='local-reviewer',
        credential_origin='local-reviewer-process')
    env_path = Path(__file__).resolve().parents[1] / '.env'
    if env_path.exists() and not os.environ.get('ASSEMBLYAI_API_KEY'):
        for line in env_path.read_text(encoding='utf-8-sig').splitlines():
            if line.startswith('ASSEMBLYAI_API_KEY='):
                os.environ['ASSEMBLYAI_API_KEY'] = line.split('=', 1)[1].strip()
    sockets, children = [], []
    try:
        sockets.append(_bind_with_fallback(args.participant_port))
        sockets.append(_bind_with_fallback(args.reviewer_port))
        broker_origin = 'http://127.0.0.1:' + str(sockets[0].getsockname()[1])
        reviewer_origin = 'http://127.0.0.1:' + str(sockets[1].getsockname()[1])
        participant_token, reviewer_token = secrets.token_urlsafe(32), secrets.token_urlsafe(32)
        context = mp.get_context('spawn')
        receive, send = context.Pipe(duplex=False)
        reviewer = context.Process(target=_reviewer,
            args=(send, broker_origin, reviewer_origin, reviewer_token, sockets[1]))
        reviewer.start()
        children.append(reviewer)
        send.close()
        if not receive.poll(15):
            raise RuntimeError('reviewer startup failed')
        public_bytes = receive.recv_bytes()
        receive.close()
        broker = context.Process(target=_broker,
            args=(public_bytes, participant_token, reviewer_token, broker_origin, sockets[0],
                  args.contact_identity))
        broker.start()
        children.append(broker)
        # Give users capabilities on their own terminal, never in public files.
        print('Participant: ' + broker_origin + '/#token=' + participant_token, flush=True)
        print('Reviewer (keep separate): ' + reviewer_origin + '/#token=' + reviewer_token, flush=True)
        print('Local demo only. Keys expire on restart. Ctrl+C stops both processes.', flush=True)
        print('Saved contact: ' + args.contact_identity +
              '. Synthetic startup enrollment; one operator may still control both roles.', flush=True)
        while all(child.is_alive() for child in children):
            time.sleep(0.25)
        raise RuntimeError('one service stopped; restart both services')
    except KeyboardInterrupt:
        return 0
    finally:
        for child in children:
            if child.is_alive():
                child.terminate()
            child.join(timeout=5)
        for sock in sockets:
            sock.close()


if __name__ == '__main__':
    raise SystemExit(main())
