'use client';

import React, { useState, useRef, useEffect, useCallback } from 'react';
import {
  Send, X, MessageCircle, Loader2, Phone, Mail, Download,
  User, MessageSquare,
} from 'lucide-react';

// ─── Types ────────────────────────────────────────────────────────────────────

interface Message {
  id        : string;
  role      : 'user' | 'assistant';
  content   : string;
  timestamp : Date;
}

interface UserDetails {
  name  : string;
  phone : string;
  email : string;
  query : string;
}

type ChatStep =
  | 'welcome'
  | 'collect_name'
  | 'collect_phone'
  | 'collect_email'
  | 'collect_query'
  | 'chat';

interface ChatbotWidgetProps {
  /** Base API url — lead endpoint = `${apiBase}/chat/lead/` (the only API call this widget makes) */
  apiBase        ?: string;
  brandColor     ?: string;
  brandName      ?: string;
  companyName    ?: string;
  phoneNumber    ?: string;
  email          ?: string;
  whatsappNumber ?: string;
  brochureUrl    ?: string;
  brochureLabel  ?: string;
  logoUrl        ?: string;
}

// ─── Session key ──────────────────────────────────────────────────────────────

function getSessionKey(): string {
  if (typeof window === 'undefined') return 'ssr';
  const KEY = 'kav_chat_session';
  let k = sessionStorage.getItem(KEY);
  if (!k) {
    k = `${Date.now()}-${Math.random().toString(36).slice(2, 10)}`;
    sessionStorage.setItem(KEY, k);
  }
  return k;
}

const LEAD_KEY = 'kav_chat_lead_date';

// ─── Bold / bullet renderer ───────────────────────────────────────────────────

function RenderMessage({ content }: { content: string }) {
  const lines = content.split('\n');
  return (
    <div>
      {lines.map((line, i) => {
        const parts = line.split(/(\*\*[^*]+\*\*)/g);
        const rendered = parts.map((part, j) => {
          if (part.startsWith('**') && part.endsWith('**')) {
            return (
              <strong key={j} style={{ fontWeight: 700 }}>
                {part.slice(2, -2)}
              </strong>
            );
          }
          return <span key={j}>{part}</span>;
        });
        return (
          <p key={i} style={{ margin: i === 0 ? 0 : '3px 0 0', lineHeight: 1.5 }}>
            {rendered}
          </p>
        );
      })}
    </div>
  );
}

// ─── Main Component ───────────────────────────────────────────────────────────

export default function ChatbotWidget({
  apiBase        = 'https://api.kavalakat.com/api',
  brandColor     = '#0077be',
  brandName      = 'AI Assistant',
  companyName    = 'Kavalakat',
  phoneNumber    = '0487 244 0380',
  email          = 'contact@kavalakat.com',
  whatsappNumber = '916238000000',
  brochureUrl    = '/kavalakat-brochure.pdf',
  brochureLabel  = 'Download Brochure',
  logoUrl        = '',
}: ChatbotWidgetProps) {

  const API_BASE = apiBase.replace(/\/$/, '');

  const [isOpen,      setIsOpen]      = useState(false);
  const [step,        setStep]        = useState<ChatStep>('welcome');
  const [inputValue,  setInputValue]  = useState('');
  const [isLoading,   setIsLoading]   = useState(false);
  const [sessionKey]                  = useState<string>(getSessionKey);
  const [messages,    setMessages]    = useState<Message[]>([]);
  const [userDetails, setUserDetails] = useState<UserDetails>({
    name: '', phone: '', email: '', query: '',
  });

  const messagesEndRef = useRef<HTMLDivElement>(null);
  const inputRef       = useRef<HTMLInputElement>(null);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, isLoading]);

  useEffect(() => {
    if (isOpen && step !== 'welcome') {
      setTimeout(() => inputRef.current?.focus(), 300);
    }
  }, [isOpen, step]);

  // ── Message helpers ────────────────────────────────────────────────────────

  const pushAssistantMsg = (content: string) =>
    setMessages(prev => [...prev, {
      id: `${Date.now()}-a`, role: 'assistant', content, timestamp: new Date(),
    }]);

  const pushUserMsg = (content: string) =>
    setMessages(prev => [...prev, {
      id: `${Date.now()}-u`, role: 'user', content, timestamp: new Date(),
    }]);

  // ── Contact handlers ───────────────────────────────────────────────────────

  const handleCall = useCallback(() => {
    window.location.href = `tel:${phoneNumber.replace(/\s/g, '')}`;
  }, [phoneNumber]);

  const handleEmail = useCallback(() => {
    window.location.href = `mailto:${email}`;
  }, [email]);

  const handleWhatsApp = useCallback(() => {
    window.open(`https://wa.me/${whatsappNumber}`, '_blank');
  }, [whatsappNumber]);

  const handleBrochure = useCallback(() => {
    const a    = document.createElement('a');
    a.href     = brochureUrl;
    a.download = `${companyName}-Brochure.pdf`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
  }, [brochureUrl, companyName]);

  // ── Start chat (welcome → workflow) ────────────────────────────────────────

  const startChat = () => {
    // Lead already submitted today → skip straight to free chat
    const lastSubDate = typeof window !== 'undefined'
      ? localStorage.getItem(LEAD_KEY)
      : null;

    if (lastSubDate === new Date().toDateString()) {
      setStep('chat');
      setMessages([]);
      setTimeout(() => pushAssistantMsg(
        `Welcome back! 👋 We have already received your query today, and our team is actively working on it.\n\nWe will be in touch with you shortly. For urgent queries, please call us at **${phoneNumber}**.`
      ), 200);
      return;
    }

    setStep('collect_name');
    setMessages([]);
    setTimeout(() => pushAssistantMsg(
      `Hi! 👋 I'm ${brandName} from ${companyName}.\n\nBefore we begin, may I know your name?`
    ), 200);
  };

  // ── Lead workflow step handlers ────────────────────────────────────────────

  const handleSubmitName = (val: string) => {
    const name = val.trim();
    if (!name) return;

    const lowerName = name.toLowerCase().replace(/[^\w\s]/g, '');
    if (['hi', 'hello', 'hey', 'hola', 'greetings'].includes(lowerName)) {
      pushUserMsg(name);
      setIsLoading(true);
      setTimeout(() => {
        setIsLoading(false);
        pushAssistantMsg('Hello! 😊 Could you please tell me your name so we can proceed?');
      }, 400);
      return;
    }

    setUserDetails(d => ({ ...d, name }));
    pushUserMsg(name);
    setIsLoading(true);
    setTimeout(() => {
      setIsLoading(false);
      setStep('collect_phone');
      pushAssistantMsg(`Nice to meet you, **${name}**! 🙌\n\nCould you please share your phone number so our team can reach you?`);
    }, 700);
  };

  const handleSubmitPhone = (val: string) => {
    const phone = val.trim();
    if (!phone) return;

    if (!/^[6-9]\d{9}$/.test(phone)) {
      pushUserMsg(phone);
      setTimeout(() => pushAssistantMsg('Please enter a valid **10-digit** Indian mobile number (starting with 6–9). 📱'), 400);
      return;
    }

    setUserDetails(d => ({ ...d, phone }));
    pushUserMsg(phone);
    setIsLoading(true);
    setTimeout(() => {
      setIsLoading(false);
      setStep('collect_email');
      pushAssistantMsg('Great! ✅ What is your **email address**? We will send the details there.');
    }, 700);
  };

  const handleSubmitEmail = (val: string) => {
    const emailVal = val.trim();
    if (!emailVal) return;

    if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(emailVal)) {
      pushUserMsg(emailVal);
      setTimeout(() => pushAssistantMsg('Hmm, that does not look like a valid email address. Could you double-check? ✉️'), 400);
      return;
    }

    setUserDetails(d => ({ ...d, email: emailVal }));
    pushUserMsg(emailVal);
    setIsLoading(true);
    setTimeout(() => {
      setIsLoading(false);
      setStep('collect_query');
      pushAssistantMsg('Perfect! 🎯 How can we help you today?\n\nPlease describe your query below.');
    }, 700);
  };

  const handleSubmitQuery = async (val: string) => {
    const query = val.trim();
    if (!query || isLoading) return;

    const payload = { ...userDetails, query, session_key: sessionKey };
    setUserDetails(prev => ({ ...prev, query }));
    pushUserMsg(query);
    setIsLoading(true);

    // ── Send lead to backend ──
    try {
      const res = await fetch(`${API_BASE}/chat/lead/`, {
        method : 'POST',
        headers: { 'Content-Type': 'application/json' },
        body   : JSON.stringify(payload),
      });
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      localStorage.setItem(LEAD_KEY, new Date().toDateString());
    } catch (err) {
      console.error('Failed to save chatbot lead:', err);
      // Continue anyway — don't block the user from chatting
    }

    setTimeout(() => {
      setIsLoading(false);
      setStep('chat');
      pushAssistantMsg(
        `Thank you, **${payload.name}**! ✅\n\nWe have noted your query: "${query}"\n\nOur team will contact you at **${payload.phone}** shortly. For urgent queries, please call us at **${phoneNumber}**.`
      );
    }, 600);
  };

  // ── After lead is saved: no AI / website data — canned team reply only ──────

  const sendChatMessage = useCallback((overrideText?: string) => {
    const text = (overrideText ?? inputValue).trim();
    if (!text || isLoading) return;

    pushUserMsg(text);
    if (!overrideText) setInputValue('');
    setIsLoading(true);

    setTimeout(() => {
      setIsLoading(false);
      pushAssistantMsg(
        `Thank you for your message. ✅\n\nWe have received your details and our team will contact you shortly.\n\nFor urgent queries, please call us at **${phoneNumber}**.`
      );
    }, 900);
  }, [inputValue, isLoading, phoneNumber]);

  // ── Unified send router ────────────────────────────────────────────────────

  const handleSendMessage = () => {
    if (!inputValue.trim() || isLoading) return;
    const value = inputValue.trim();
    setInputValue('');

    switch (step) {
      case 'collect_name':  return handleSubmitName(value);
      case 'collect_phone': return handleSubmitPhone(value);
      case 'collect_email': return handleSubmitEmail(value);
      case 'collect_query': return handleSubmitQuery(value);
      case 'chat':          return sendChatMessage(value);
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  const getPlaceholder = () => {
    switch (step) {
      case 'collect_name':  return 'Enter your full name...';
      case 'collect_phone': return 'Enter 10-digit mobile number...';
      case 'collect_email': return 'Enter your email address...';
      case 'collect_query': return 'Describe your query...';
      default:              return 'Type your message...';
    }
  };

  const showProgress = ['collect_name', 'collect_phone', 'collect_email', 'collect_query'].includes(step);

  // ── Side button styles ────────────────────────────────────────────────────

  const sideBtn: React.CSSProperties = {
    width         : '48px',
    height        : '48px',
    borderRadius  : '24px',
    color         : 'white',
    border        : 'none',
    cursor        : 'pointer',
    display       : 'flex',
    alignItems    : 'center',
    justifyContent: 'flex-start',
    paddingLeft   : '12px',
    paddingRight  : '12px',
    gap           : '10px',
    boxShadow     : '0 4px 12px rgba(0,0,0,0.18)',
    transition    : 'all 0.28s cubic-bezier(0.4,0,0.2,1)',
    overflow      : 'hidden',
    whiteSpace    : 'nowrap',
    fontSize      : '13px',
    fontWeight    : '600',
  };

  const labelStyle: React.CSSProperties = {
    opacity   : 0,
    maxWidth  : '0',
    overflow  : 'hidden',
    transition: 'opacity 0.28s ease, max-width 0.28s ease',
  };

  const expandBtn = (e: React.MouseEvent<HTMLButtonElement>) => {
    const el = e.currentTarget;
    el.style.width        = 'auto';
    el.style.paddingRight = '16px';
    el.style.transform    = 'translateX(-4px)';
    const span = el.querySelector<HTMLSpanElement>('.btn-label');
    if (span) { span.style.opacity = '1'; span.style.maxWidth = '200px'; }
  };

  const collapseBtn = (e: React.MouseEvent<HTMLButtonElement>) => {
    const el = e.currentTarget;
    el.style.width        = '48px';
    el.style.paddingRight = '12px';
    el.style.transform    = 'translateX(0)';
    const span = el.querySelector<HTMLSpanElement>('.btn-label');
    if (span) { span.style.opacity = '0'; span.style.maxWidth = '0'; }
  };

  // ─────────────────────────────────────────────────────────────────────────

  return (
    <div>

      {/* ── Side buttons ──────────────────────────────────────────────────── */}
      <div style={{
        position      : 'fixed',
        right         : '1rem',
        top           : '50%',
        transform     : 'translateY(-50%)',
        zIndex        : 9999,
        display       : 'flex',
        flexDirection : 'column',
        gap           : '10px',
        alignItems    : 'flex-end',
      }}>

        {/* Brochure */}
        <button onClick={handleBrochure}
          style={{ ...sideBtn, backgroundColor: '#e67e22' }}
          onMouseEnter={expandBtn} onMouseLeave={collapseBtn}
          aria-label={brochureLabel} title={brochureLabel}>
          <Download size={20} style={{ flexShrink: 0 }} />
          <span className="btn-label" style={labelStyle}>{brochureLabel}</span>
        </button>

        {/* WhatsApp */}
        <button onClick={handleWhatsApp}
          style={{ ...sideBtn, backgroundColor: '#25D366' }}
          onMouseEnter={expandBtn} onMouseLeave={collapseBtn}
          aria-label="WhatsApp" title="WhatsApp">
          <svg width="20" height="20" fill="currentColor" viewBox="0 0 24 24" style={{ flexShrink: 0 }}>
            <path d="M17.472 14.382c-.297-.149-1.758-.867-2.03-.967-.273-.099-.471-.148-.67.15-.197.297-.767.966-.94 1.164-.173.199-.347.223-.644.075-.297-.15-1.255-.463-2.39-1.475-.883-.788-1.48-1.761-1.653-2.059-.173-.297-.018-.458.13-.606.134-.133.298-.347.446-.52.149-.174.198-.298.298-.497.099-.198.05-.371-.025-.52-.075-.149-.669-1.612-.916-2.207-.242-.579-.487-.5-.669-.51-.173-.008-.371-.01-.57-.01-.198 0-.52.074-.792.372-.272.297-1.04 1.016-1.04 2.479 0 1.462 1.065 2.875 1.213 3.074.149.198 2.096 3.2 5.077 4.487.709.306 1.262.489 1.694.625.712.227 1.36.195 1.871.118.571-.085 1.758-.719 2.006-1.413.248-.694.248-1.289.173-1.413-.074-.124-.272-.198-.57-.347m-5.421 7.403h-.004a9.87 9.87 0 01-5.031-1.378l-.361-.214-3.741.982.998-3.648-.235-.374a9.86 9.86 0 01-1.51-5.26c.001-5.45 4.436-9.884 9.888-9.884 2.64 0 5.122 1.03 6.988 2.898a9.825 9.825 0 012.893 6.994c-.003 5.45-4.437 9.884-9.885 9.884m8.413-18.297A11.815 11.815 0 0012.05 0C5.495 0 .16 5.335.157 11.892c0 2.096.547 4.142 1.588 5.945L.057 24l6.305-1.654a11.882 11.882 0 005.683 1.448h.005c6.554 0 11.89-5.335 11.893-11.893a11.821 11.821 0 00-3.48-8.413Z"/>
          </svg>
          <span className="btn-label" style={labelStyle}>WhatsApp</span>
        </button>

        {/* Phone */}
        <button onClick={handleCall}
          style={{ ...sideBtn, backgroundColor: brandColor }}
          onMouseEnter={expandBtn} onMouseLeave={collapseBtn}
          aria-label={`Call ${phoneNumber}`} title={phoneNumber}>
          <Phone size={20} style={{ flexShrink: 0 }} />
          <span className="btn-label" style={labelStyle}>{phoneNumber}</span>
        </button>

        {/* Email */}
        <button onClick={handleEmail}
          style={{ ...sideBtn, backgroundColor: brandColor }}
          onMouseEnter={expandBtn} onMouseLeave={collapseBtn}
          aria-label={`Email ${email}`} title={email}>
          <Mail size={20} style={{ flexShrink: 0 }} />
          <span className="btn-label" style={labelStyle}>{email}</span>
        </button>

        {/* Chat toggle */}
        <button
          onClick={() => setIsOpen(v => !v)}
          style={{
            ...sideBtn,
            backgroundColor: brandColor,
            boxShadow: isOpen ? `0 4px 20px ${brandColor}66` : '0 4px 12px rgba(0,0,0,0.18)',
          }}
          onMouseEnter={expandBtn} onMouseLeave={collapseBtn}
          aria-label={isOpen ? 'Close chat' : 'Open chat'}>
          {isOpen ? (
            <><X size={20} style={{ flexShrink: 0 }} />
            <span className="btn-label" style={labelStyle}>Close Chat</span></>
          ) : (
            <><MessageCircle size={20} style={{ flexShrink: 0 }} />
            <span className="btn-label" style={labelStyle}>Chat with us</span></>
          )}
        </button>
      </div>

      {/* ── Chat window ───────────────────────────────────────────────────── */}
      {isOpen && (
        <div
          className="kav-window"
          role="dialog"
          aria-label="Chat Assistant"
          aria-modal="true"
          style={{
            position        : 'fixed',
            top             : '50%',
            right           : '80px',
            transform       : 'translateY(-50%)',
            zIndex          : 9998,
            width           : '390px',
            maxWidth        : 'calc(100vw - 100px)',
            height          : '620px',
            maxHeight       : 'calc(100vh - 40px)',
            backgroundColor : 'white',
            borderRadius    : '18px',
            boxShadow       : '0 25px 60px rgba(0,0,0,0.2), 0 4px 16px rgba(0,0,0,0.08)',
            display         : 'flex',
            flexDirection   : 'column',
            overflow        : 'hidden',
            border          : '1px solid #e5e7eb',
            animation       : 'kavSlideIn 0.3s cubic-bezier(0.34,1.56,0.64,1)',
          }}
        >

          {/* Header */}
          <div style={{
            padding    : '14px 16px',
            background : `linear-gradient(135deg, ${brandColor} 0%, ${brandColor}dd 100%)`,
            color      : 'white',
            display    : 'flex',
            alignItems : 'center',
            justifyContent: 'space-between',
            flexShrink : 0,
          }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
              <div style={{
                width: '42px', height: '42px', borderRadius: '50%',
                backgroundColor: 'rgba(255,255,255,0.2)',
                display: 'flex', alignItems: 'center', justifyContent: 'center',
                flexShrink: 0, overflow: 'hidden',
              }}>
                {logoUrl
                  ? <img src={logoUrl} alt={companyName} style={{ width: '65%', height: '65%', objectFit: 'contain' }} />
                  : <MessageCircle size={21} />
                }
              </div>
              <div>
                <h3 style={{ fontWeight: 700, fontSize: '1rem', margin: 0, lineHeight: 1.2 }}>
                  {brandName}
                </h3>
                <p style={{
                  fontSize: '0.78rem', opacity: 0.9, margin: '3px 0 0',
                  display: 'flex', alignItems: 'center', gap: '5px',
                }}>
                  <span style={{
                    display: 'inline-block', width: '7px', height: '7px',
                    borderRadius: '50%', background: '#4ade80',
                    animation: 'kavPulse 2s infinite',
                  }} />
                  Online now
                </p>
              </div>
            </div>
            <button onClick={() => setIsOpen(false)} aria-label="Close chat"
              style={{
                background: 'rgba(255,255,255,0.15)', border: 'none', color: 'white',
                cursor: 'pointer', width: '32px', height: '32px', borderRadius: '8px',
                display: 'flex', alignItems: 'center', justifyContent: 'center',
                transition: 'background 0.2s',
              }}
              onMouseEnter={e => (e.currentTarget.style.background = 'rgba(255,255,255,0.3)')}
              onMouseLeave={e => (e.currentTarget.style.background = 'rgba(255,255,255,0.15)')}>
              <X size={18} />
            </button>
          </div>

          {/* ── Welcome screen ── */}
          {step === 'welcome' ? (
            <div style={{
              flex: 1, display: 'flex', flexDirection: 'column',
              alignItems: 'center', justifyContent: 'center',
              padding: '30px 20px', background: '#f8fafc', gap: '18px',
              overflowY: 'auto',
            }}>
              {/* Logo / icon */}
              <div style={{
                width: '76px', height: '76px', borderRadius: '22px',
                background: `linear-gradient(135deg, ${brandColor} 0%, ${brandColor}cc 100%)`,
                display: 'flex', alignItems: 'center', justifyContent: 'center',
                boxShadow: `0 10px 28px ${brandColor}44`,
                overflow: 'hidden',
              }}>
                {logoUrl
                  ? <img src={logoUrl} alt={companyName} style={{ width: '70%', height: '70%', objectFit: 'contain' }} />
                  : <MessageCircle size={36} color="white" />
                }
              </div>

              <div style={{ textAlign: 'center' }}>
                <h2 style={{
                  fontSize: '1.25rem', fontWeight: 700, color: '#0f172a',
                  margin: '0 0 6px',
                }}>
                  Welcome to {companyName}
                </h2>
                <p style={{ fontSize: '0.84rem', color: '#64748b', margin: 0, lineHeight: 1.55 }}>
                  We are here to help you with your queries, quotes,
                  and everything about our services.
                </p>
              </div>

              {/* Feature list */}
              <div style={{ display: 'flex', flexDirection: 'column', gap: '8px', width: '100%' }}>
                {[
                  { icon: <MessageSquare size={15} />, text: 'Instant answers to your questions' },
                  { icon: <User size={15} />,          text: 'Personalised assistance from our team' },
                  { icon: <Phone size={15} />,         text: 'Quick callback on your query' },
                ].map((item, i) => (
                  <div key={i} style={{
                    display: 'flex', alignItems: 'center', gap: '10px',
                    background: '#fff', borderRadius: '10px', padding: '10px 12px',
                    border: '1px solid #e2e8f0',
                    fontSize: '0.82rem', color: '#374151',
                  }}>
                    <span style={{ color: brandColor, flexShrink: 0 }}>{item.icon}</span>
                    {item.text}
                  </div>
                ))}
              </div>

              <button
                onClick={startChat}
                style={{
                  background: brandColor, color: '#fff', border: 'none',
                  borderRadius: '12px', padding: '13px 28px',
                  fontSize: '0.92rem', fontWeight: 600, cursor: 'pointer',
                  width: '100%', display: 'flex', alignItems: 'center',
                  justifyContent: 'center', gap: '8px',
                  boxShadow: `0 6px 18px ${brandColor}55`,
                  transition: 'transform .18s, box-shadow .18s',
                }}
                onMouseEnter={e => (e.currentTarget.style.transform = 'translateY(-2px)')}
                onMouseLeave={e => (e.currentTarget.style.transform = 'translateY(0)')}
              >
                Start Chat <Send size={16} />
              </button>

              <p style={{ fontSize: '0.68rem', color: '#94a3b8', margin: 0, textAlign: 'center' }}>
                By continuing you agree to our Privacy Policy
              </p>
            </div>
          ) : (
            <>
              {/* ── Messages ── */}
              <div role="log" aria-live="polite" style={{
                flex: 1, overflowY: 'auto', padding: '14px',
                backgroundColor: '#f8fafc',
                display: 'flex', flexDirection: 'column', gap: '10px',
              }}>

                {/* Step banner */}
                {showProgress && (
                  <div style={{
                    background: `${brandColor}0f`,
                    border: `1px dashed ${brandColor}40`,
                    borderRadius: '10px', padding: '8px 12px',
                    fontSize: '0.75rem', color: brandColor,
                    display: 'flex', alignItems: 'center', gap: '7px', flexShrink: 0,
                    fontWeight: 500,
                  }}>
                    {step === 'collect_name'  && <><User size={13} /> Step 1 of 4 — Your name</>}
                    {step === 'collect_phone' && <><Phone size={13} /> Step 2 of 4 — Phone number</>}
                    {step === 'collect_email' && <><Mail size={13} /> Step 3 of 4 — Email address</>}
                    {step === 'collect_query' && <><MessageSquare size={13} /> Step 4 of 4 — Your query</>}
                  </div>
                )}

                {messages.map(msg => (
                  <div key={msg.id} style={{
                    display: 'flex',
                    justifyContent: msg.role === 'user' ? 'flex-end' : 'flex-start',
                    animation: 'kavFadeIn 0.22s ease',
                  }}>
                    <div style={{
                      maxWidth       : '80%',
                      borderRadius   : msg.role === 'user' ? '16px 16px 4px 16px' : '4px 16px 16px 16px',
                      padding        : '10px 14px',
                      backgroundColor: msg.role === 'user' ? brandColor : 'white',
                      color          : msg.role === 'user' ? 'white' : '#1e293b',
                      border         : msg.role === 'assistant' ? '1px solid #e2e8f0' : 'none',
                      boxShadow      : msg.role === 'assistant'
                        ? '0 1px 4px rgba(0,0,0,0.06)'
                        : `0 2px 8px ${brandColor}33`,
                    }}>
                      <div style={{ fontSize: '0.875rem', margin: 0, wordBreak: 'break-word' }}>
                        <RenderMessage content={msg.content} />
                      </div>
                      <span style={{
                        fontSize: '0.67rem', opacity: 0.55, marginTop: '5px',
                        display: 'block', textAlign: msg.role === 'user' ? 'right' : 'left',
                      }}>
                        {msg.timestamp.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                      </span>
                    </div>
                  </div>
                ))}

                {/* Typing dots */}
                {isLoading && (
                  <div style={{ display: 'flex', justifyContent: 'flex-start', animation: 'kavFadeIn 0.2s ease' }}>
                    <div style={{
                      backgroundColor: 'white', border: '1px solid #e2e8f0',
                      borderRadius: '4px 16px 16px 16px', padding: '12px 16px',
                      display: 'flex', alignItems: 'center', gap: '5px',
                      boxShadow: '0 1px 4px rgba(0,0,0,0.06)',
                    }}>
                      {[0, 160, 320].map(delay => (
                        <span key={delay} style={{
                          width: '7px', height: '7px', borderRadius: '50%',
                          backgroundColor: brandColor, opacity: 0.6,
                          display: 'inline-block',
                          animation: `kavBounce 1.2s ${delay}ms infinite`,
                        }} />
                      ))}
                    </div>
                  </div>
                )}

                {/* Saved details card */}
                {step === 'chat' && userDetails.name && (
                  <div style={{
                    background: `${brandColor}0d`,
                    border: `1px solid ${brandColor}26`,
                    borderRadius: '14px', padding: '12px 14px',
                    fontSize: '0.78rem', color: '#374151',
                  }}>
                    <div style={{
                      fontWeight: 600, color: brandColor, marginBottom: '8px',
                      fontSize: '0.68rem', textTransform: 'uppercase',
                      letterSpacing: '0.06em',
                    }}>
                      Contact Details Confirmed
                    </div>
                    <div style={{ display: 'flex', flexDirection: 'column', gap: '5px' }}>
                      <span style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
                        <User size={12} style={{ color: brandColor, flexShrink: 0 }} /> {userDetails.name}
                      </span>
                      <span style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
                        <Phone size={12} style={{ color: brandColor, flexShrink: 0 }} /> {userDetails.phone}
                      </span>
                      <span style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
                        <Mail size={12} style={{ color: brandColor, flexShrink: 0 }} /> {userDetails.email}
                      </span>
                    </div>
                  </div>
                )}

                <div ref={messagesEndRef} />
              </div>

              {/* ── Input bar ── */}
              <div style={{
                padding        : '12px 14px',
                backgroundColor: 'white',
                borderTop      : '1px solid #f1f5f9',
                display        : 'flex',
                gap            : '8px',
                flexShrink     : 0,
              }}>
                <input
                  ref={inputRef}
                  type={step === 'collect_email' ? 'email' : step === 'collect_phone' ? 'tel' : 'text'}
                  value={inputValue}
                  onChange={e => setInputValue(e.target.value)}
                  onKeyDown={handleKeyDown}
                  placeholder={getPlaceholder()}
                  disabled={isLoading}
                  maxLength={step === 'collect_phone' ? 10 : undefined}
                  aria-label={getPlaceholder()}
                  style={{
                    flex        : 1,
                    padding     : '10px 14px',
                    border      : '1.5px solid #e2e8f0',
                    borderRadius: '10px',
                    fontSize    : '0.875rem',
                    outline     : 'none',
                    fontFamily  : 'inherit',
                    transition  : 'border-color 0.2s, box-shadow 0.2s',
                    color       : '#1e293b',
                    background  : '#f8fafc',
                    opacity     : isLoading ? 0.6 : 1,
                  }}
                  onFocus={e => {
                    e.currentTarget.style.borderColor = brandColor;
                    e.currentTarget.style.boxShadow   = `0 0 0 3px ${brandColor}20`;
                    e.currentTarget.style.background  = '#fff';
                  }}
                  onBlur={e => {
                    e.currentTarget.style.borderColor = '#e2e8f0';
                    e.currentTarget.style.boxShadow   = 'none';
                    e.currentTarget.style.background  = '#f8fafc';
                  }}
                />
                <button
                  onClick={handleSendMessage}
                  disabled={!inputValue.trim() || isLoading}
                  aria-label="Send"
                  style={{
                    width          : '42px',
                    height         : '42px',
                    borderRadius   : '10px',
                    backgroundColor: !inputValue.trim() || isLoading ? '#cbd5e1' : brandColor,
                    color          : 'white',
                    border         : 'none',
                    cursor         : !inputValue.trim() || isLoading ? 'not-allowed' : 'pointer',
                    display        : 'flex',
                    alignItems     : 'center',
                    justifyContent : 'center',
                    flexShrink     : 0,
                    transition     : 'all 0.15s',
                    boxShadow      : !inputValue.trim() || isLoading ? 'none' : `0 2px 8px ${brandColor}44`,
                  }}
                  onMouseEnter={e => {
                    if (!inputValue.trim() || isLoading) return;
                    e.currentTarget.style.transform = 'scale(1.08)';
                  }}
                  onMouseLeave={e => {
                    e.currentTarget.style.transform = 'scale(1)';
                  }}
                >
                  {isLoading
                    ? <Loader2 size={17} style={{ animation: 'kavSpin 0.8s linear infinite' }} />
                    : <Send size={17} />
                  }
                </button>
              </div>
            </>
          )}

          {/* Footer */}
          <div style={{
            textAlign: 'center', fontSize: '0.66rem', color: '#94a3b8',
            padding: '5px 0 8px', backgroundColor: 'white', flexShrink: 0,
            borderTop: '1px solid #f3f4f6',
          }}>
            Powered by <strong style={{ color: brandColor }}>{companyName}</strong> · Your data is secure
          </div>

        </div>
      )}

      {/* Animations + mobile fullscreen */}
      <style>{`
        @keyframes kavSlideIn {
          from { opacity: 0; transform: translateY(calc(-50% + 24px)) scale(0.96); }
          to   { opacity: 1; transform: translateY(-50%) scale(1); }
        }
        @keyframes kavFadeIn {
          from { opacity: 0; transform: translateY(8px); }
          to   { opacity: 1; transform: translateY(0); }
        }
        @keyframes kavBounce {
          0%, 60%, 100% { transform: translateY(0); }
          30%           { transform: translateY(-6px); }
        }
        @keyframes kavSpin {
          from { transform: rotate(0deg); }
          to   { transform: rotate(360deg); }
        }
        @keyframes kavPulse {
          0%, 100% { opacity: 1; }
          50%      { opacity: 0.5; }
        }

        /* ── Responsive: phones & tablets → fullscreen chat ── */
        @media (max-width: 899px) {
          .kav-window {
            top: 0 !important; left: 0 !important;
            right: 0 !important; bottom: 0 !important;
            width: 100vw !important; max-width: 100vw !important;
            height: 100dvh !important; max-height: 100dvh !important;
            border-radius: 0 !important;
            transform: none !important;
            animation: kavFadeIn 0.25s ease !important;
          }
          .kav-window input { font-size: 16px !important; }
        }
      `}</style>
    </div>
  );
}
