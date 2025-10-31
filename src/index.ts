import { Hono } from 'hono';
import { getSandbox, Sandbox } from '@cloudflare/sandbox';

interface CmdOutput {
  success: boolean;
  stdout: string;
  stderr: string;
}

interface RequestPayload {
  repo: string;
  task: string;
}

interface Env {
  Sandbox: DurableObjectNamespace<Sandbox>;
  ANTHROPIC_API_KEY: string;
}

const EXTRA_SYSTEM =
  'You are an automatic feature-implementer/bug-fixer.' +
  'You apply all necessary changes to achieve the user request. You must ensure you DO NOT commit the changes, ' +
  'so the pipeline can read the local `git diff` and apply the change upstream.';

const app = new Hono<{ Bindings: Env }>();

const getOutput = (result: CmdOutput) =>
  result.success ? result.stdout : result.stderr;

const sanitizeTask = (task: string) => task.replaceAll('"', '\\"');

app.get('/health', (c) => c.json({ ok: true }));

app.post('/sandbox/run', async (c) => {
  let payload: Partial<RequestPayload>;
  try {
    payload = await c.req.json<RequestPayload>();
  } catch (error) {
    console.error('Invalid JSON payload', error);
    return c.json({ error: 'invalid_json' }, 400);
  }

  const { repo, task } = payload ?? {};
  if (!repo || !task) {
    return c.json({ error: 'repo_and_task_required' }, 400);
  }

  let repoUrl: URL;
  try {
    repoUrl = new URL(repo);
  } catch (error) {
    console.error('Invalid repository URL', error);
    return c.json({ error: 'invalid_repo_url' }, 400);
  }

  const name = repoUrl.pathname.split('/').filter(Boolean).pop() ?? 'workspace';
  const sandbox = getSandbox(c.env.Sandbox, crypto.randomUUID().slice(0, 8));

  try {
    await sandbox.gitCheckout(repoUrl.toString(), { targetDir: name });
    await sandbox.setEnvVars({ ANTHROPIC_API_KEY: c.env.ANTHROPIC_API_KEY });

    const command =
      `cd ${name} && claude --append-system-prompt "${EXTRA_SYSTEM}" ` +
      `-p "${sanitizeTask(task)}" --permission-mode acceptEdits`;

    const logs = getOutput(await sandbox.exec(command));
    const diff = getOutput(await sandbox.exec('git diff'));

    return c.json({ logs, diff });
  } catch (error) {
    console.error('Sandbox execution error', error);
    return c.json({ error: 'sandbox_execution_failed' }, 500);
  }
});

app.notFound((c) => c.json({ error: 'not_found' }, 404));

app.onError((err, c) => {
  console.error('Unhandled error', err);
  return c.json({ error: 'internal_error' }, 500);
});

export default app;
export { Sandbox };
