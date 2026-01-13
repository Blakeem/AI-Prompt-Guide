---
name: spec-external
description: "Document 3rd party APIs/components from official sources. Use when integrating SDKs, webhooks, auth flows, or documenting external service contracts."
allowed-tools:
  - Read
  - Write
  - Edit
  - Glob
  - Grep
  - WebFetch
  - WebSearch
  - TodoWrite
---

# Workflow: Document External API Specification

**Arguments:** $ARGUMENTS

## [Research Phase]

1. **Identify authoritative sources**
   - Official documentation
   - API references
   - RFCs if applicable
   - Match runtime/environment versions

2. **Extract API contract from source documentation:**
   - Capabilities and features
   - Invariants and constraints
   - Limits (rate limits, size limits, timeouts)
   - Error semantics (codes, retry policies)
   - Version compatibility gates
   - Authentication requirements

## [Documentation Phase]

3. **Create specification document with these sections:**
   - API Overview
   - Authentication
   - Endpoints with signatures
   - Request/response formats with examples
   - Error conditions and handling
   - Rate limits and quotas
   - Version compatibility

4. **Include for each endpoint:**
   - HTTP method and path
   - Request parameters
   - Request body schema
   - Response schema
   - Error responses
   - Example request/response

## [Acceptance Criteria]

5. **Define acceptance criteria:**
   - Happy path tests
   - Edge cases (boundaries, limits)
   - Error handling per specification
   - Performance requirements (latency/throughput)

## Specification Template

```markdown
# External API: [Service Name]

## Overview
- **Service:** [Name]
- **Version:** [Version]
- **Documentation:** [URL]
- **Last Updated:** [Date]

## Authentication
- **Method:** [OAuth2 / API Key / etc.]
- **Header:** `Authorization: Bearer {token}`
- **Scopes:** [List required scopes]

## Endpoints

### [Endpoint Name]
**`METHOD /path/to/endpoint`**

**Request:**
```json
{
  "field": "type - description"
}
```

**Response (200):**
```json
{
  "field": "type - description"
}
```

**Errors:**
| Code | Meaning | Handling |
|------|---------|----------|
| 400  | Bad request | Validate input |
| 401  | Unauthorized | Refresh token |
| 429  | Rate limited | Retry with backoff |

## Rate Limits
- **Requests:** X per minute
- **Burst:** Y requests
- **Retry-After:** Header included on 429

## Version Compatibility
- **Minimum version:** X.Y.Z
- **Deprecation notes:** [Any deprecated features]

## Acceptance Criteria
- [ ] Authentication flow works
- [ ] Happy path returns expected format
- [ ] Rate limiting handled with backoff
- [ ] Errors return expected codes
```

## Principles

- Official docs are truth
- Spec compliance before simplicity
- Test against specification, not assumptions
- Document version-specific behavior
- Include real examples from official docs
