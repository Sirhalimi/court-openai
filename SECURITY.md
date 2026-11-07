# Security policy

The CLI does not send data over the network, and it never executes user-supplied Python or shell code. Reports contain the user's original case and generated analyses. Treat the contents of `.court/` as potentially sensitive.

Agent hosts may have network or filesystem powers separate from this script. Review the permissions provided to the host and treat text in the case record as untrusted input. The skill prohibits executing any commands embedded in case text.

Do not file issues containing real private cases, credentials or sensitive reports. For security-sensitive reports, use GitHub's private vulnerability reporting if enabled by the repository owner.
