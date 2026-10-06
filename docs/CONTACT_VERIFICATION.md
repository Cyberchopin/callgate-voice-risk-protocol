# Claimed identity and saved-contact verification

Implemented: trusted-startup contact routing for the local simulator. Not implemented: independent human enrollment, phone delivery, identity-provider authentication, revocation, or real payments.

## Run it

Run `python -m scripts.start_review_demo`. Startup creates a synthetic `saved-family` entry with the reviewer child's public key. To give the fictional identity a different identifier, run `python -m scripts.start_review_demo --contact-identity fictional-parent`.

Open the printed participant and reviewer links on the trusted host. Grant processing consent, submit `Send money.`, click **读取已登记联系人**, select the caller's claimed identity, and request confirmation for a fictional amount/destination. The reviewer checks the displayed identity and operation, receives the challenge through the agreed separate demo channel, and approves or denies. Approval only completes a simulation.

Unknown or omitted identities are rejected in the launcher. There is no contact enrollment endpoint and speech cannot add keys. The identity selection is an explicit participant input; the system does not claim to extract identity reliably from a transcript.

## Binding and trust

`ContactDirectory` is supplied by trusted startup. Each `SavedContact` binds a stable identity identifier to a reviewer and a credential-origin identifier. Origins are enrollment records, not HTTP Origin headers, client JSON, or proof of physical device ownership. The coordinator rejects a contact with the same origin as the session initiator; it also rejects reuse of a signing key across saved reviewers.

The operation digest commits to destination, amount, currency and claimed identity. The signed confirmation includes that digest, session, selected reviewer, claimed identity, random request identifier, and expiry. The request identifier supplies fresh nonce material. The issuer only signs after a matching registered reviewer decision; the gate consumes the resulting credential once. Client-selected reviewers cannot override the directory route.

Denial and observed timeout prevent further authorization for that session, including identity or amount changes. Status and pending-request reads observe expiry and clear expired requests. An explicit new demo session is a new scenario, not a production way to rehabilitate a denied transaction.

The broker capability is scoped to its configured reviewer route; a request addressed to another contact is neither returned to it nor accepted from it. The reviewer UI also checks its expected addressee and the identity/operation commitment before signing.

## Boundaries

- The launcher has one synthetic saved contact and one reviewer process. Multiple registered keys are supported and tested in the coordinator, but multi-contact delivery and remote devices are not implemented.
- Startup generates both role entry URLs on the same trusted host. An operator may hold both. This increment rejects recorded same-origin credentials, not all self-approval by one human controlling different credentials.
- Startup enrollment records can be wrong. Account/key compromise, collusion, recovery, revocation and persistent authorization state remain unresolved.
- Restart invalidates ephemeral keys and pending requests. No claim of durable production denial across restart is made.
- Legacy programmatic coordinator instances without a directory remain available for archived tests and the protocol rehearsal. They do not acquire saved-contact guarantees; a claimed identity is rejected if no directory is configured.
- No predictions were run on prospective blind evaluation inputs and no new warning-coverage or legitimate-request utility metric is asserted.

## Verify

Run `python -m pytest tests/test_contact_binding.py tests/test_review_process.py -q -p no:cacheprovider`. These cover routing, same-origin rejection, wrong-key signatures, modified identity/session/resource/nonce, replay, expiry, denial, scoped reviewer capabilities, and actual loopback HTTP completion through the spawned processes.
