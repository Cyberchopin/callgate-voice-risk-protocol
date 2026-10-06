"""Signed reviewer confirmation for a local demo; no human login is implemented.

Reviewer public keys and issuer private key are provisioned by trusted startup.
The reviewer signs the exact server-created request on a separate trusted client.
Pending requests are disposable: restarting the coordinator invalidates them.
"""
import json
import secrets
import threading
import time
from typing import Literal
from pydantic import Field
from cryptography.exceptions import InvalidSignature
from .models import StrictModel
from .verification import VerificationClaim, issue_for_demo


class ConfirmationRequest(StrictModel):
    version: Literal["callgate-confirmation-v1"] = "callgate-confirmation-v1"
    request_id: str
    reviewer: str
    session_id: str
    resource: str
    action: Literal["simulate_protected_action"] = "simulate_protected_action"
    issued_at: int
    expires_at: int


class ReviewerDecision(StrictModel):
    request: ConfirmationRequest
    approved: bool
    signature: str = Field(pattern=r"^[a-f0-9]{128}$")


def decision_bytes(request, approved):
    return json.dumps({"request":request.model_dump(), "approved":approved},
                      sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode("ascii")


class ConfirmationCoordinator:
    def __init__(self, issuer, signing_key, reviewers, *, clock=time.time):
        self._issuer, self._signing_key = issuer, signing_key
        self._reviewers = dict(reviewers)
        self._clock = clock
        self._pending = {}
        self._lock = threading.Lock()

    def create(self, *, session_id, resource, reviewer):
        """Trusted orchestration selects reviewer; caller speech cannot enroll keys."""
        if reviewer not in self._reviewers:
            raise ValueError("unknown reviewer")
        now = int(self._clock())
        # Reuse the credential schema's bounded scope validation before storing.
        VerificationClaim(issuer=self._issuer, session_id=session_id, resource=resource,
                          issued_at=now, expires_at=now+120, nonce=secrets.token_hex(32))
        request = ConfirmationRequest(request_id=secrets.token_hex(32), reviewer=reviewer,
            session_id=session_id, resource=resource, issued_at=now, expires_at=now+120)
        with self._lock:
            self._pending = {k:v for k,v in self._pending.items() if v.expires_at > now}
            if len(self._pending) >= 1000:
                raise ValueError("confirmation capacity reached")
            self._pending[request.request_id] = request
        return request

    def expired(self, request):
        """Trusted clock query; never accept a client-provided current time."""
        return int(self._clock()) >= request.expires_at

    def decide(self, decision):
        decision = ReviewerDecision.model_validate(decision)
        with self._lock:
            request = self._pending.get(decision.request.request_id)
            if request is None or request != decision.request:
                raise ValueError("unknown or modified request")
            now = int(self._clock())
            if not request.issued_at <= now < request.expires_at:
                raise ValueError("confirmation expired or not yet valid")
            key = self._reviewers[request.reviewer]
            try:
                key.verify(bytes.fromhex(decision.signature), decision_bytes(request, decision.approved))
            except InvalidSignature:
                raise ValueError("invalid reviewer signature") from None
            if not decision.approved:
                del self._pending[request.request_id]
                return None
            credential = issue_for_demo(self._signing_key, issuer=self._issuer,
                session_id=request.session_id, resource=request.resource, now=now)
            del self._pending[request.request_id]
            return credential

    def cancel(self, request_id):
        """Trusted orchestration discards superseded confirmation requests."""
        with self._lock:
            self._pending.pop(request_id, None)
