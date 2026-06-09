# Spec axis brief

You are one axis of a multi-axis code review. Review **only** the diff below against the originating spec.

- Spec: `{spec path or contents}`
- Diff: `{diff command}`
- Commits: `{commit list}`

Read the spec, then the diff. Report:

- (a) requirements the spec asked for that are missing or partial;
- (b) behaviour in the diff that wasn't asked for (scope creep);
- (c) requirements that look implemented but where the implementation looks wrong.

Quote the spec line for each finding.

First read [_contract.md](_contract.md) and follow it for report length and finding format.
