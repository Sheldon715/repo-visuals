# Security

repo-visuals is designed to keep repository inspection and final image composition local.

- The bundled Python scripts do not make network requests.
- Do not send source files, secrets, environment files, or private repository content to an image-generation service.
- Send only the compact artwork prompt and reference images explicitly approved for that purpose.
- Review every installed Skill and script before running it, as you would any other development dependency.

To report a vulnerability, open a private security advisory on the GitHub repository after publication. Do not include credentials, private source code, or sensitive user data in a public issue.
