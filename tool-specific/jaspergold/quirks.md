# JasperGold Specifics

> 🔬 **from-docs** — This file holds release-specific observations. Revalidate every command form against the installed release before standardizing it in a flow.

## Hunt Strategy Listing and Display [JG-specific]

🔧 **VERSION-SENSITIVE — validated on JasperGold 2025.12p002.** `hunt -list
strategy` returns the built-in strategy names, but it rejects `-silent` with
`ERROR (ESW104): Invalid command formation` for `-list -silent`. Do not infer
that a switch accepted by another Jasper command is accepted by this form.

```tcl
# Valid: returns a Tcl list of strategy names.
set strategies [hunt -list strategy]

# Valid in 2025.12p002: suppresses display while returning resolved settings.
set settings [hunt -show -strategy <bound_swarm> -silent]
```

`hunt -show -strategy <name>` also works without `-silent`. Keep the no-switch
form in portable examples unless the installed release has been checked.

## Planned Content

- GUI vs batch mode differences
- License feature requirements per app
- Integration with Verdi for debug
- Performance tips and known issues
- File format specifics (jdb, etc.)
