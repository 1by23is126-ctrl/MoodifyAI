import React, { useEffect, useRef, useState } from 'react';
import { loginWithGoogle, logout as logoutRequest, getSpotifyAuthorizeUrl } from '../utils/api';

export default function AuthPanel({ user, onUserUpdate, onLogout, onError }) {
  const buttonContainerRef = useRef(null);
  const [googleReady, setGoogleReady] = useState(false);
  const [loading, setLoading] = useState(false);
  const initRef = useRef(false);
  const clientId = import.meta.env.VITE_GOOGLE_CLIENT_ID;

  useEffect(() => {
    if (!clientId) {
      setGoogleReady(false);
      return;
    }

    const tryInitialize = () => {
      if (initRef.current || !window.google?.accounts?.id) {
        return;
      }

      initRef.current = true;
      window.google.accounts.id.initialize({
        client_id: clientId,
        callback: async (response) => {
          if (!response?.credential) return;
          setLoading(true);
          try {
            const payload = await loginWithGoogle(response.credential);
            onUserUpdate(payload.user);
          } catch (err) {
            onError?.(err.message || 'Google sign in failed.');
          } finally {
            setLoading(false);
          }
        },
        cancel_on_tap_outside: true,
      });

      if (buttonContainerRef.current) {
        window.google.accounts.id.renderButton(buttonContainerRef.current, {
          theme: 'outline',
          size: 'large',
          type: 'standard',
          text: 'signin_with',
        });
      }

      setGoogleReady(true);
    };

    const intervalId = setInterval(tryInitialize, 500);
    tryInitialize();
    return () => clearInterval(intervalId);
  }, [clientId, onError, onUserUpdate]);

  const handleLogout = async () => {
    setLoading(true);
    try {
      await logoutRequest();
      onLogout();
    } catch (err) {
      onError?.(err.message || 'Logout failed.');
    } finally {
      setLoading(false);
    }
  };

  const handleSpotifyConnect = async () => {
    setLoading(true);
    try {
      const payload = await getSpotifyAuthorizeUrl();
      if (payload?.authorize_url) {
        window.location.href = payload.authorize_url;
      } else {
        throw new Error('Spotify authorize URL not available.');
      }
    } catch (err) {
      onError?.(err.message || 'Could not start Spotify connection.');
      setLoading(false);
    }
  };

  return (
    <div className="auth-panel flex flex-wrap items-center gap-3 p-3 rounded-full bg-black/30 border border-white/10 shadow-[0_30px_120px_rgba(0,0,0,0.15)] backdrop-blur-xl">
      {user ? (
        <>
          <div className="flex items-center gap-3">
            <img src={user.picture || '/icons/user-circle.svg'} alt="User avatar" className="w-9 h-9 rounded-full object-cover" />
            <div className="text-left">
              <p className="text-sm font-semibold">{user.name || user.email}</p>
              <p className="text-[11px] text-muted">{user.spotify?.spotify_user_id ? 'Spotify connected' : 'Spotify disconnected'}</p>
            </div>
          </div>
          <button
            type="button"
            onClick={handleSpotifyConnect}
            disabled={loading}
            className="btn-secondary px-4 py-2 rounded-full text-[0.78rem] font-semibold"
          >
            {user.spotify?.spotify_user_id ? 'Reconnect Spotify' : 'Connect Spotify'}
          </button>
          <button
            type="button"
            onClick={handleLogout}
            disabled={loading}
            className="btn-secondary px-4 py-2 rounded-full text-[0.78rem] font-semibold"
          >
            Sign Out
          </button>
        </>
      ) : (
        <div className="flex flex-col gap-2 items-start">
          <p className="text-sm font-semibold">Sign in to save moods and journals</p>
          <div ref={buttonContainerRef} />
          {!clientId && (
            <div className="text-xs text-muted">Set VITE_GOOGLE_CLIENT_ID to enable Google authentication.</div>
          )}
          {googleReady && <div className="text-xs text-muted">Use the Google button above to sign in.</div>}
          {!googleReady && clientId && (
            <div className="text-xs text-muted">Loading Google auth…</div>
          )}
        </div>
      )}
    </div>
  );
}
