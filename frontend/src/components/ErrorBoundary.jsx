import React from 'react';

export default class ErrorBoundary extends React.Component {
  constructor(props) {
    super(props);
    this.state = { hasError: false };
  }

  static getDerivedStateFromError() {
    return { hasError: true };
  }

  componentDidCatch(error, errorInfo) {
    console.error('MoodifyAI render error:', error, errorInfo);
  }

  render() {
    if (this.state.hasError) {
      return (
        <div className="flex min-h-screen items-center justify-center bg-void px-6 text-center">
          <div className="glass-card max-w-xl rounded-3xl border border-white/10 p-10">
            <p className="readable-kicker mb-3 text-xs font-semibold uppercase tracking-[0.3em]">Recovery mode</p>
            <h2 className="mb-4 text-3xl font-semibold text-white">Something glitched in the experience.</h2>
            <p className="mb-8 text-sm leading-relaxed text-secondary">
              MoodifyAI recovered gracefully, but the current view hit an unexpected runtime issue. Refreshing usually restores the experience instantly.
            </p>
            <button
              type="button"
              onClick={() => window.location.reload()}
              className="rounded-full border border-white/10 bg-white/10 px-5 py-2 text-sm font-medium text-white transition hover:bg-white/20"
            >
              Refresh experience
            </button>
          </div>
        </div>
      );
    }

    return this.props.children;
  }
}
