# hermes-plugin-solstice

Solstice model provider for [Hermes Agent](https://github.com/NousResearch/hermes-agent): run Hermes on your
own per-user Gemini quota, signed in with Google through the Nous portal.

This plugin used to ship inside Hermes (`plugins/model-providers/solstice/`). It now lives in its own repo,
so new models and fixes reach you as soon as they land here instead of waiting for a Hermes release.
Version 0.2.0 adds **Gemini 4 Argon** (`gemini-4-argon`).

Solstice is pre-release. It stays out of the provider pickers, setup lists and accounts tab until you sign in
by name. After that it is listed like any other signed-in provider.

## Requirements

- Hermes Agent **0.22.0 or newer** (`hermes --version`). Argon's request handling (thinking level, resuming
  long answers) is in Hermes core and arrived in 0.22.0. The plugin refuses to install on older releases.
- A Nous Portal sign-in (`hermes auth add nous`) on an account with Solstice access.

## Install

```bash
hermes plugins install NousResearch/hermes-plugin-solstice
hermes auth add solstice          # skip this if you already signed in to the built-in version
hermes model                      # or: hermes config set model.provider solstice
```

The plugin starts working as soon as it is installed. It is a model-provider plugin, so it needs no
`hermes plugins enable`. If the installer says "installed but not enabled", ignore it; `hermes plugins list`
shows it as `enabled`.

Plugins are installed per profile. For a named profile, add `-p <profile>` to each command:
`hermes -p work plugins install NousResearch/hermes-plugin-solstice`.

To try a model directly:

```bash
hermes chat --provider solstice -m gemini-4-argon
```

Models offered: `gemini-3.1-pro` (default), `gemini-4-argon`, `gemini-3.8-flash`, `gemini-3.5-flash-lite`.
Each model has its own quota. When a model runs out, Google returns HTTP 429 or 402 ("usage limit"). Switch
to another model; Flash Lite is listed last as the one to fall back to.

## Migrating from the built-in version

If you already use Solstice on Hermes 0.22.x, installing this plugin is the whole migration.

1. Check your version: `hermes --version` must say 0.22.0 or newer. If not, run `hermes update` first.
2. `hermes plugins install NousResearch/hermes-plugin-solstice` (repeat with `-p <profile>` for each profile
   that uses Solstice).
3. Restart anything that is running Hermes so it loads the plugin: the gateway (`hermes gateway restart`),
   the desktop app, and any open `hermes` sessions.
4. Check it is active:

   ```bash
   hermes plugins list | grep solstice                 # solstice ... enabled ... 0.2.0 ... git
   hermes chat --provider solstice -m gemini-4-argon -q "hi" --oneshot
   ```

What carries over without any action:

- **Your sign-in.** The plugin registers the same provider name (`solstice`, alias `solstice-oauth`) and reads
  the same saved credential in `auth.json`. You do not sign in again.
- **Your config.** `model.provider: solstice`, saved model choices, fallback chains and cron jobs that name
  `solstice` keep working unchanged.

Why this is safe on a release that still bundles Solstice: when a plugin in your `~/.hermes/plugins/`
registers a provider with the same name as a built-in one, Hermes uses the installed plugin. The bundled copy
is still on disk, but it is no longer used.

### Updating

```bash
hermes plugins update solstice
```

Then restart running Hermes processes as in step 3.

### Going back to the built-in version

```bash
hermes plugins remove solstice
```

Hermes falls back to the copy bundled with your release (without Gemini 4 Argon on 0.22.2 and earlier). Your
sign-in and config are unaffected.

### Hosted and locked-down installs

The plugin runs inside the Hermes process. If you have set `plugins.isolation: host` in `config.yaml`, Hermes
refuses to load it, because its client cannot be moved into the separate plugin process. In that case it
keeps using the bundled copy, if your release has one. `hermes plugins validate` reports this as
"Isolation — in-process only".

## How it works

- **Sign-in** (`auth.py`): browser PKCE with a loopback redirect. The Nous portal brokers the token exchange
  and refresh because it holds the Google client secret. Hermes keeps its own PKCE verifier and your tokens.
  The portal never sees a prompt.
- **Inference** (`transport.py`): Hermes's native Gemini client, sent to Google's per-user-quota methods
  (`:generateContentPerUserQuota` / `:streamGenerateContentPerUserQuota`) with your OAuth access token instead
  of an API key.
- **Models** (`__init__.py`): a fixed list, because the per-user-quota endpoint has no model listing a user
  token is allowed to read.

The plugin imports some Hermes internals (`agent.gemini_native_adapter`, parts of `hermes_cli.auth`).
`hermes plugins validate` lists them as warnings. That coupling is why the plugin declares a minimum Hermes
version; check new Hermes releases against these tests.

## Development

Tests run against a Hermes checkout, using its test runner:

```bash
cd /path/to/hermes-agent
scripts/run_tests.sh /path/to/hermes-plugin-solstice/tests/test_solstice_profile.py
```

Each test installs this repo into a temporary `$HERMES_HOME` and asserts that this repo's profile, not a
bundled copy, is the one under test. When invoking pytest some other way, `HERMES_AGENT_REPO` picks the
checkout; otherwise the current directory is used if it is a Hermes checkout, then `~/.hermes/hermes-agent`.

To release: bump `version` in `plugin.yaml`, merge to `main`. Users pick it up with `hermes plugins update
solstice`.

History before the move is preserved from `NousResearch/hermes-agent`.
