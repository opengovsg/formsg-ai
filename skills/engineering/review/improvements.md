To maintain: 
- the idea of spawning multiple sub-agents that prevent context pollution and keeps the context window focused. 
- the idea of aggregating the reports from the multiple subagents 
- the idea of not merging axes so the user can evaluate them independently
- keep the current 2 axes, make necessary improvements only if necessary based on To improve section.  

To improve: 
- the standards subagent should after checking documented standards, seek to zoom out and understand standards across the repo and make recommendations. question if these standards are tech debt before following them. prioritise documented standards over 

For example, if the code is using a hack or clearly incorrect practice, do not follow it without careful consideration. 


- add more axes as its own independent subagents to get a more complete picture for aggregation. 
new axis: using the recommendations in the /improve-codebase-architecture skill, determine if there can be improvements to the changes in this PR. 

for example, 
Suggestion (not blocking): decide “is this the new format?” one consistent way.

Today the code answers that question two different ways: (a) by peeking inside the data for a provenance key (isFieldResponsesV4), and (b) by reading the saved mrfVersion number. This line uses both, joined with &&. Elsewhere in the app, mrfVersion gets read with four different comparisons: === 1, === 2, != null, and !mrfVersion.

Why this bites later: when the two checks disagree — e.g. an empty response, or some future version number — the && makes this silently fall back to “treat it as the old format,” which is the wrong answer on a security check. And because the same mrfVersion number is interpreted four different ways, every reader is re-deciding what each number means; the day someone adds mrfVersion: 3, they have to find and re-check all of them.

Suggestion: pick the saved mrfVersion as the single source of truth and wrap it in one tiny helper (e.g. isV4(submission)), used everywhere. Keep the provenance peek only as the SDK’s internal fallback for old data that has no mrfVersion. (This also resolves the unresolved //TODO on this line.)

🤖 This is an AI-generated architecture suggestion — non-blocking, please sanity-check before acting on it.

Member
@kevin9foong
kevin9foong
yesterday
• 
thoughts: this is related to review comment regarding the reuse of the exported isFieldResponseV4 above. resolving the above might help with this

refer to https://github.com/opengovsg/FormSG/pull/9502 and its PR comments and review for references. 

new axis: practice divergent thinking. consider why each change was made and its theme and question if it is the best choice out of the alternatives. However, also consider the scope of the PR and if it makes sense to make this change now. (/zoom-out if you have to in order to get a full picture)

initially, the PR comment by AI was: 

const _mod = require('./dist/cjs/index.js')
module.exports = _mod.default
// Re-export named exports so CJS consumers can access them
Object.keys(_mod).forEach((key) => {
Member
@kevin9foong
kevin9foong
yesterday
Nit / edge case: copying named exports onto the default function object works, but a named export colliding with an intrinsic function property (name, length) would be silently skipped or clobbered. Fine for the current export names — just noting it in case the export surface grows.


after prompting the model to understand if this change is required and if it differs from how we were doing it previously. is this really ideal? 

the ideal suggestion: 
suggestion: instead of adding a loop which copies named exports onto the default factory function so CJS consumers (the backend) can reach adaptV3ToV4 / adaptV4ToV3. Shall we use the current packages/sdk/package.json subpath export approach instead to keep things consistent?

For context, "./dist/types" also faced the same issue which was resolved with subpath exports, similar to our formsg-shared package.

Suggested addition to packages/sdk/package.json:

"./adapters": {
  "import":  { "types": "./dist/esm/adapters.d.ts", "default": "./dist/esm/adapters.js" },
  "require": { "types": "./dist/cjs/adapters.d.ts", "default": "./dist/cjs/adapters.js" }
}
This achieves 2 benefits:

prevents potential named export colliding with an intrinsic function property (name, length) which would be silently skipped or clobbered. Fine for the current export names — but noting it in case the export surface grows.
Prevents having 2 different methods in the codebase of resolving these named exports
Member
Author
@scottheng96
scottheng96
2 hours ago
Thanks for surfacing this. I agree that the loop solution wasn't optimal, but didn't find another approach after time boxing this. Learnt something and happy to keep things consistent with how we're already doing it.

- refer to the /code-review skill from anthropics and its recommendations on false positives. implement some version of it with comments (it makes sense to do it directly on the LoC in Github PR for easier reference). consider adding a summary comment if it adds value (eg, what to focus on, what was covered etc). 

Some pointers: 
- include an AI review disclaimer when commenting (Eg, 🤖 This comment was generated by an AI code review. Please verify before acting on it.)
- follow conventional review for comments, for eg, praise, nit etc
- mental alignment with the reviewer and code author is important, explain the rationale behind each suggestion clearly referencing the /unslop skill from cursor to do so. 

examples of a concise PR comment: 
question: since this is a one-way door, shall we clean up/remove this function as well? we can always recover the code from Github commit history.
keeping it might make it unclear which decryption pipeline is canonical.

previous (using unclear terms, eg altitude):
Architectural suggestion (altitude): expose the adapters via a subpath export instead of decorating the factory function.

This loop copies named exports onto the default factory function so CJS consumers (the backend) can reach adaptV3ToV4 / adaptV4ToV3. It works, but it's a workaround for overloading one entry point with two unrelated responsibilities: a callable default (the configured SDK factory) and stateless utility functions. Hanging utilities off the function object is what creates the intrinsic-property-collision footgun (name, length, …) and makes the package's runtime export surface implicit.

There's already an in-package precedent for the cleaner approach. packages/sdk/package.json ships a subpath export "./dist/types" whose require condition resolves to a plain compiled CJS module (./dist/cjs/types.js) — not through this cjs-entry.cjs flatten shim. Its named exports therefore resolve natively, with no decoration and no collision risk. (formsg-shared uses this same subpath pattern at scale.) The only entry that has to flatten is ".", precisely because it carries the legacy "the module is the factory function" contract — the adapters don't need that contract.

Suggested shape — add a subpath alongside the existing ones:

"./adapters": {
  "import":  { "types": "./dist/esm/adapters.d.ts", "default": "./dist/esm/adapters.js" },
  "require": { "types": "./dist/cjs/adapters.d.ts", "default": "./dist/cjs/adapters.js" }
}
Backend then imports import { adaptV3ToV4 } from '@opengovsg/formsg-sdk/adapters', the require condition hits a normal CJS namespace, named values resolve natively — and cjs-entry.cjs can go back to its original one-liner (no loop, no collision caveat).

Not a blocker for this PR — the current approach unblocks the backend. But it follows the repo's own established pattern rather than introducing a decorate-the-function approach that has no precedent here. If keeping the single entry for now, prefer explicit named assignments over the dynamic loop so the export surface is legible and intrinsic-name collisions surface instead of silently no-op'ing.

🤖 This comment was generated by an AI code review. Please verify before acting on it. 

better: 
suggestion: instead of adding a loop which copies named exports onto the default factory function so CJS consumers (the backend) can reach adaptV3ToV4 / adaptV4ToV3. Shall we use the current packages/sdk/package.json subpath export approach instead to keep things consistent?

For context, "./dist/types" also faced the same issue which was resolved with subpath exports, similar to our formsg-shared package.

Suggested addition to packages/sdk/package.json:

"./adapters": {
  "import":  { "types": "./dist/esm/adapters.d.ts", "default": "./dist/esm/adapters.js" },
  "require": { "types": "./dist/cjs/adapters.d.ts", "default": "./dist/cjs/adapters.js" }
}
This achieves 2 benefits:

prevents potential named export colliding with an intrinsic function property (name, length) which would be silently skipped or clobbered. Fine for the current export names — but noting it in case the export surface grows.
Prevents having 2 different methods in the codebase of resolving these named exports

Note: 
- when improving this review skill, refer to the recommendations in /write-a-skill to ensure this skill will perform optimally. 
