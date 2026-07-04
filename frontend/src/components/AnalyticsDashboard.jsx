import React, { useEffect, useState } from 'react';
import { motion } from 'framer-motion';
import { ResponsiveContainer, AreaChart, Area, XAxis, YAxis, Tooltip, CartesianGrid } from 'recharts';
import { MOOD_COLORS } from '../hooks/useMoodTheme';
import { getMoodAnalytics, loadMoodHistory } from '../utils/storage';

export default function AnalyticsDashboard({ onBack }) {
  const [analytics, setAnalytics] = useState(null);
  const [history, setHistory] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    setLoading(true);
    try {
      setAnalytics(getMoodAnalytics());
      setHistory(loadMoodHistory().slice(0, 20));
    } catch (error) {
      console.error('Failed to load analytics', error);
      setAnalytics(null);
    } finally {
      setLoading(false);
    }
  }, []);

  const chartData = analytics?.weeklyTrend?.map((item) => ({
    name: item.date.slice(5),
    count: item.count
  })) || [];

  const moodDistribution = analytics?.moodDistribution || [];
  const topMood = analytics?.favoriteMood || '—';
  const language = analytics?.favoriteLanguage || '—';
  const artists = analytics?.mostRecommendedArtists || [];
  const insights = analytics?.insights || [];

  const chartColor = MOOD_COLORS[topMood]?.primary || 'var(--mood-primary)';

  const containerVariants = {
    hidden: { opacity: 0 },
    visible: { opacity: 1, transition: { staggerChildren: 0.08, delayChildren: 0.05 } }
  };

  const itemVariants = {
    hidden: { opacity: 0, y: 16, filter: 'blur(6px)' },
    visible: { opacity: 1, y: 0, filter: 'blur(0px)', transition: { duration: 0.6, ease: [0.16, 1, 0.3, 1] } }
  };

  return (
    <div className="w-full max-w-6xl mx-auto flex flex-col gap-7 relative z-20 pb-20 px-4">
      <motion.div
        initial={{ opacity: 0, y: -8 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.6, ease: [0.16, 1, 0.3, 1] }}
        className="flex items-end justify-between px-2 gap-4 flex-wrap"
      >
        <div>
          <span className="readable-kicker text-[10px] tracking-[0.24em] uppercase font-semibold text-muted">
            Analytics · mood history
          </span>
          <h2 className="text-stellar text-[2rem] md:text-[2.4rem] font-display font-semibold tracking-[-0.025em] mt-1">
            Emotional <span className="editorial-italic font-normal">trajectory</span>
          </h2>
        </div>
        <button
          onClick={onBack}
          className="btn-secondary px-5 py-2.5 rounded-full flex items-center gap-2 text-[0.78rem] font-semibold tracking-[0.04em]"
          data-testid="analytics-back"
        >
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.2" strokeLinecap="round" strokeLinejoin="round">
            <path d="M19 12H5M12 19l-7-7 7-7"/>
          </svg>
          Back
        </button>
      </motion.div>

      {loading ? (
        <div className="flex justify-center py-24">
          <div className="relative w-10 h-10">
            <div className="absolute inset-0 rounded-full border border-white/10" />
            <div className="absolute inset-0 rounded-full border border-transparent border-t-[var(--mood-primary)] animate-spin" />
          </div>
        </div>
      ) : (
        <motion.div
          variants={containerVariants}
          initial="hidden"
          animate="visible"
          className="grid grid-cols-1 lg:grid-cols-3 gap-5"
        >
          <motion.div variants={itemVariants} className="analytics-card lg:col-span-2 rounded-[22px] p-6 h-[420px] flex flex-col">
            <div className="flex items-center justify-between mb-5">
              <div>
                <h3 className="analytics-label text-[10px]">Weekly mood trend</h3>
                <p className="text-xs text-muted mt-1">Activity over the last 7 days</p>
              </div>
              <span className="text-[10px] text-muted font-medium tracking-[0.14em] uppercase">{analytics?.weeklyTrend?.length || 0} days</span>
            </div>
            <div className="flex-1 w-full min-h-0">
              <ResponsiveContainer width="100%" height="100%">
                <AreaChart data={chartData} margin={{ top: 8, right: 8, left: -18, bottom: 0 }}>
                  <defs>
                    <linearGradient id="colorVal" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="0%" stopColor={chartColor} stopOpacity={0.48}/>
                      <stop offset="100%" stopColor={chartColor} stopOpacity={0}/>
                    </linearGradient>
                  </defs>
                  <CartesianGrid strokeDasharray="2 4" stroke="rgba(255,255,255,0.05)" vertical={false} />
                  <XAxis dataKey="name" stroke="rgba(255,255,255,0.18)" tick={{ fill: 'var(--text-muted)', fontSize: 10 }} />
                  <YAxis stroke="rgba(255,255,255,0.18)" tick={{ fill: 'var(--text-muted)', fontSize: 10 }} />
                  <Tooltip
                    contentStyle={{
                      backgroundColor: 'rgba(10,12,18,0.92)',
                      border: '1px solid rgba(255,255,255,0.12)',
                      borderRadius: '12px',
                      backdropFilter: 'blur(20px)',
                      boxShadow: '0 18px 48px rgba(0,0,0,0.5)',
                      fontSize: '12px'
                    }}
                    itemStyle={{ color: '#fff' }}
                    labelStyle={{ display: 'none' }}
                  />
                  <Area type="monotone" dataKey="count" stroke={chartColor} strokeWidth={2.2} fillOpacity={1} fill="url(#colorVal)" dot={false} />
                </AreaChart>
              </ResponsiveContainer>
            </div>
          </motion.div>

          <motion.div variants={itemVariants} className="flex flex-col gap-5">
            <div className="analytics-card rounded-[22px] p-6 flex-1 flex flex-col justify-between">
              <div>
                <span className="analytics-label text-[10px] mb-3">Total analyses</span>
                <span className="text-[3rem] font-display font-semibold tracking-[-0.04em] text-gradient-mood leading-none tabular-nums">
                  {analytics?.totalEntries ?? 0}
                </span>
              </div>
              <span className="mt-3 text-[11px] text-muted tracking-[0.12em]">mood sessions recorded</span>
            </div>

            <div className="analytics-card rounded-[22px] p-6 flex-1 flex flex-col justify-between">
              <div>
                <span className="analytics-label text-[10px] mb-3">Favorite language</span>
                <span className="text-[1.6rem] font-display font-semibold tracking-[-0.018em] text-stellar leading-none">
                  {language}
                </span>
              </div>
              <span className="mt-3 text-[11px] text-muted tracking-[0.12em]">most listened mood language</span>
            </div>
          </motion.div>

          <motion.div variants={itemVariants} className="analytics-card lg:col-span-3 rounded-[22px] p-6 mt-2">
            <div className="flex items-center justify-between mb-5 gap-4 flex-wrap">
              <div>
                <h3 className="analytics-label text-[10px]">Insights</h3>
                <p className="text-xs text-muted mt-1">Personalized observations from your mood history</p>
              </div>
              <span className="text-[10px] text-muted font-medium tracking-[0.14em] uppercase">{artists.length} top artists</span>
            </div>
            <div className="grid gap-4 md:grid-cols-2">
              {insights.length > 0 ? (
                insights.map((insight, index) => (
                  <div key={index} className="rounded-3xl border border-white/10 bg-slate-950/70 p-4 text-sm text-muted">
                    {insight}
                  </div>
                ))
              ) : (
                <div className="rounded-3xl border border-white/10 bg-slate-950/70 p-4 text-sm text-muted">
                  Add more mood entries to unlock deeper insights.
                </div>
              )}
            </div>
          </motion.div>

          <motion.div variants={itemVariants} className="analytics-card lg:col-span-3 rounded-[22px] p-6 mt-2">
            <div className="flex items-center justify-between mb-5">
              <div>
                <h3 className="analytics-label text-[10px]">Mood distribution</h3>
                <p className="text-xs text-muted mt-1">Your emotional balance over time</p>
              </div>
            </div>
            <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-4">
              {moodDistribution.map((item) => (
                <div key={item.mood} className="rounded-3xl border border-white/10 bg-slate-950/70 p-4 text-sm">
                  <div className="text-sm text-muted">{item.mood}</div>
                  <div className="mt-2 text-xl font-semibold text-white">{item.count}</div>
                </div>
              ))}
            </div>
          </motion.div>

          <motion.div variants={itemVariants} className="analytics-card lg:col-span-3 rounded-[22px] p-6 mt-2">
            <div className="flex items-center justify-between mb-5">
              <div>
                <h3 className="analytics-label text-[10px]">Recent mood entries</h3>
                <p className="text-xs text-muted mt-1">Latest tracks and records</p>
              </div>
            </div>
            <div className="flex flex-col gap-3 max-h-[320px] overflow-y-auto pr-2">
              {history.length === 0 ? (
                <div className="text-center py-14 text-sm text-muted">No mood records available yet.</div>
              ) : (
                history.map((item, index) => (
                  <div key={`${item.id || index}-${index}`} className="analytics-row flex items-center gap-4 p-3.5 rounded-xl border border-white/10 bg-slate-950/70">
                    <div
                      className="w-2.5 h-2.5 rounded-full flex-shrink-0"
                      style={{ background: MOOD_COLORS[item.mood]?.primary || '#fff' }}
                    />
                    <div className="min-w-0">
                      <p className="text-sm font-medium text-stellar truncate">{item.mood}</p>
                      <p className="text-[11px] text-muted truncate">{item.prompt}</p>
                    </div>
                    <div className="text-[10px] text-muted whitespace-nowrap tracking-[0.06em] tabular-nums">
                      {item.timestamp ? new Date(item.timestamp).toLocaleDateString([], { month: 'short', day: 'numeric' }) : ''}
                    </div>
                  </div>
                ))
              )}
            </div>
          </motion.div>
        </motion.div>
      )}
    </div>
  );
}
