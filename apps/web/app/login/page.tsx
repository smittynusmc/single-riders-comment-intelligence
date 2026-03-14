import { LoginForm } from "@/components/auth/login-form";

export default function LoginPage() {
  return (
    <div className="flex min-h-[80vh] items-center justify-center px-4 py-12">
      <div className="w-full max-w-3xl space-y-6">
        <div className="text-center">
          <p className="text-xs uppercase tracking-[0.3em] text-slate">Private Internal Access</p>
          <h1 className="mt-3 font-display text-4xl font-semibold text-ink">MVP Audience Insights</h1>
          <p className="mt-3 text-base text-slate">
            Hosted on Vercel and Railway for the internal Single Riders team. Sign in to review shared imports, audience signals, and roadmap evidence.
          </p>
        </div>
        <LoginForm />
      </div>
    </div>
  );
}
