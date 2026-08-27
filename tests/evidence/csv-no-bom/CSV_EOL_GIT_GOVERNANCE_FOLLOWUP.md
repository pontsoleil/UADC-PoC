# CSV EOL Git Governance Follow-up

The Formal UADC-PoC repository currently contains `*.csv text eol=lf` in
`.gitattributes`. The file was inspected read-only and was not changed.

This rule can make a staged blob differ from approved Candidate CSV bytes when
those bytes contain CRLF. Before Formal placement, a separate governance change
must assess rule precedence and affected tracked paths. The proposed rule is:

```gitattributes
*.csv -text
```

No actual `.gitattributes` edit, renormalization, stage, commit, or push is
authorized by this report.
