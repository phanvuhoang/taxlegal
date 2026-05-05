import React, { useState, useEffect, useRef, useCallback } from 'react';
import { Send, Plus, ExternalLink, MessageSquare } from 'lucide-react';
import { legalaiApi } from '../lib/legalai';

interface Message {
  id?: string;
  role: 'user' | 'assistant';
  content: string;
  citations?: any[];
  model?: string;
  created_at?: string;
}

interface Session {
  id: string;
  title: string;
  agent_type: string;
  updated_at: string;
}

const QUICK_QUESTIONS = [
  'Thuế GTGT hàng hóa xuất khẩu là bao nhiêu?',
  'Điều kiện khấu trừ chi phí thuế TNDN?',
  'Quy định về thuế nhà thầu nước ngoài?',
  'Khai thuế TNCN từ lương như thế nào?',
];

// Simple markdown rendering (bold, citations, line breaks)
function renderContent(text: string) {
  const html = text
    .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
    .replace(/\[(\d+)\]/g, '<sup style="color:#028a39;font-weight:700">[$1]</sup>')
    .replace(/\n/g, '<br/>');
  return { __html: html };
}

export default function LegalChat() {
  const [sessions, setSessions] = useState<Session[]>([]);
  const [currentSession, setCurrentSession] = useState<string | null>(null);
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [loadingSessions, setLoadingSessions] = useState(true);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    loadSessions();
  }, []);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const loadSessions = async () => {
    try {
      const res = await legalaiApi.listSessions();
      setSessions(res.data.sessions || []);
    } catch {
      setSessions([]);
    } finally {
      setLoadingSessions(false);
    }
  };

  const loadMessages = async (sessionId: string) => {
    try {
      const res = await legalaiApi.getMessages(sessionId);
      setMessages(res.data.messages || []);
    } catch {
      setMessages([]);
    }
  };

  const selectSession = (sessionId: string) => {
    setCurrentSession(sessionId);
    loadMessages(sessionId);
  };

  const newChat = async () => {
    try {
      const res = await legalaiApi.createSession();
      const sessionId = res.data.session_id;
      setCurrentSession(sessionId);
      setMessages([]);
      await loadSessions();
    } catch (e) {
      console.error(e);
    }
  };

  const sendMessage = useCallback(async (questionOverride?: string) => {
    const question = (questionOverride ?? input).trim();
    if (!question || loading) return;

    if (!questionOverride) setInput('');

    // Optimistic user message
    setMessages(prev => [...prev, { role: 'user', content: question }]);
    setLoading(true);

    try {
      let sessionId = currentSession;
      if (!sessionId) {
        const res = await legalaiApi.createSession(question.slice(0, 50));
        sessionId = res.data.session_id;
        setCurrentSession(sessionId);
        await loadSessions();
      }

      const res = await legalaiApi.askQuestion(question, sessionId ?? undefined);
      const { answer, citations, model } = res.data;

      setMessages(prev => [...prev, {
        role: 'assistant',
        content: answer,
        citations: citations || [],
        model,
      }]);
    } catch (e: any) {
      setMessages(prev => [...prev, {
        role: 'assistant',
        content: `❌ Lỗi: ${e?.response?.data?.detail || 'Không thể kết nối AI lúc này. Vui lòng kiểm tra API keys.'}`,
        citations: [],
      }]);
    } finally {
      setLoading(false);
    }
  }, [input, loading, currentSession]);

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  };

  return (
    <div className="flex h-[calc(100vh-112px)] overflow-hidden -mx-6 -my-6">
      {/* Sidebar */}
      <div className="w-60 border-r border-gray-200 bg-gray-50 flex flex-col shrink-0">
        <div className="p-3 border-b border-gray-100">
          <button
            onClick={newChat}
            className="w-full py-2 px-3 rounded-lg text-sm font-medium text-white transition-opacity hover:opacity-90 flex items-center justify-center gap-2"
            style={{ backgroundColor: '#028a39' }}
          >
            <Plus className="w-4 h-4" />
            Hội thoại mới
          </button>
        </div>

        <div className="flex-1 overflow-y-auto p-2">
          {loadingSessions ? (
            <div className="text-center py-6 text-gray-400 text-xs">Đang tải...</div>
          ) : sessions.length === 0 ? (
            <div className="text-center py-6 text-gray-400 text-xs">Chưa có hội thoại</div>
          ) : (
            sessions.map(s => (
              <button
                key={s.id}
                onClick={() => selectSession(s.id)}
                className={`w-full text-left px-3 py-2.5 rounded-lg mb-0.5 text-sm transition-colors ${
                  currentSession === s.id
                    ? 'text-white'
                    : 'text-gray-700 hover:bg-gray-200'
                }`}
                style={currentSession === s.id ? { backgroundColor: '#028a39' } : {}}
              >
                <div className="font-medium truncate text-xs leading-snug">{s.title}</div>
                <div className="text-xs opacity-60 mt-0.5">
                  {new Date(s.updated_at).toLocaleDateString('vi-VN')}
                </div>
              </button>
            ))
          )}
        </div>
      </div>

      {/* Main chat area */}
      <div className="flex-1 flex flex-col overflow-hidden bg-white">
        {/* Header bar */}
        <div className="border-b border-gray-100 px-5 py-3 flex items-center gap-3 shrink-0">
          <MessageSquare className="w-5 h-5" style={{ color: '#028a39' }} />
          <div>
            <h2 className="text-sm font-semibold text-gray-900">Trợ lý Tư vấn Thuế AI</h2>
            <p className="text-xs text-gray-400">RAG-powered · Luật thuế Việt Nam</p>
          </div>
        </div>

        {/* Messages */}
        <div className="flex-1 overflow-y-auto px-5 py-5 space-y-4">
          {messages.length === 0 && (
            <div className="text-center py-12 text-gray-400">
              <div
                className="w-14 h-14 rounded-2xl flex items-center justify-center mx-auto mb-4"
                style={{ backgroundColor: '#e6f4ec' }}
              >
                <MessageSquare className="w-7 h-7" style={{ color: '#028a39' }} />
              </div>
              <h3 className="text-base font-semibold text-gray-600 mb-1">
                Hỏi bất kỳ câu hỏi về thuế VN
              </h3>
              <p className="text-sm text-gray-400 max-w-sm mx-auto mb-6">
                CIT, VAT, PIT, thuế nhà thầu, quản lý thuế — AI sẽ trả lời có trích dẫn nguồn văn bản pháp luật.
              </p>
              <div className="grid grid-cols-2 gap-2 max-w-lg mx-auto">
                {QUICK_QUESTIONS.map(q => (
                  <button
                    key={q}
                    onClick={() => sendMessage(q)}
                    className="text-left text-xs p-3 bg-gray-50 border border-gray-200 rounded-xl hover:border-green-300 hover:bg-green-50 transition-colors leading-relaxed"
                  >
                    {q}
                  </button>
                ))}
              </div>
            </div>
          )}

          {messages.map((msg, i) => (
            <div key={i} className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}>
              <div
                className={`max-w-2xl rounded-2xl px-4 py-3 ${
                  msg.role === 'user'
                    ? 'text-white'
                    : 'bg-gray-50 border border-gray-200'
                }`}
                style={msg.role === 'user' ? { backgroundColor: '#028a39' } : {}}
              >
                {msg.role === 'assistant' ? (
                  <>
                    <div
                      className="text-sm text-gray-800 leading-relaxed"
                      dangerouslySetInnerHTML={renderContent(msg.content)}
                    />

                    {msg.citations && msg.citations.length > 0 && (
                      <div className="mt-3 pt-3 border-t border-gray-200 space-y-2">
                        <p className="text-xs font-semibold text-gray-500 uppercase tracking-wide">
                          Nguồn tham chiếu
                        </p>
                        {msg.citations.slice(0, 5).map((c: any, ci: number) => (
                          <div
                            key={ci}
                            className="bg-white rounded-lg p-2.5 text-xs border border-gray-100"
                          >
                            <div className="flex items-start gap-2 mb-1">
                              <span
                                className="font-bold shrink-0 mt-0.5"
                                style={{ color: '#028a39' }}
                              >
                                [{c.ref || ci + 1}]
                              </span>
                              <div className="min-w-0">
                                <span className="font-medium text-gray-700 block truncate">
                                  {c.law_title}
                                </span>
                                {c.law_number && (
                                  <span className="text-gray-400 font-mono text-xs">{c.law_number}</span>
                                )}
                              </div>
                            </div>
                            {(c.article || c.clause) && (
                              <p className="text-gray-500 mb-1">
                                {c.article}{c.clause ? ` — ${c.clause}` : ''}
                              </p>
                            )}
                            <p className="text-gray-600 line-clamp-2">{c.content}</p>
                            {c.source_url && (
                              <a
                                href={c.source_url}
                                target="_blank"
                                rel="noopener noreferrer"
                                className="mt-1.5 flex items-center gap-1 hover:underline w-fit"
                                style={{ color: '#028a39' }}
                              >
                                <ExternalLink className="w-3 h-3" />
                                Xem văn bản gốc
                              </a>
                            )}
                          </div>
                        ))}
                      </div>
                    )}

                    {msg.model && (
                      <p className="text-xs text-gray-400 mt-2">Model: {msg.model}</p>
                    )}
                  </>
                ) : (
                  <p className="text-sm leading-relaxed">{msg.content}</p>
                )}
              </div>
            </div>
          ))}

          {/* Loading dots */}
          {loading && (
            <div className="flex justify-start">
              <div className="bg-gray-50 border border-gray-200 rounded-2xl px-4 py-3 flex items-center gap-2">
                <div className="flex gap-1">
                  {[0, 1, 2].map(i => (
                    <div
                      key={i}
                      className="w-2 h-2 rounded-full animate-bounce"
                      style={{ backgroundColor: '#028a39', animationDelay: `${i * 0.12}s` }}
                    />
                  ))}
                </div>
                <span className="text-xs text-gray-500">Đang tra cứu và phân tích...</span>
              </div>
            </div>
          )}

          <div ref={messagesEndRef} />
        </div>

        {/* Input area */}
        <div className="border-t border-gray-100 px-5 py-4 bg-white shrink-0">
          <div className="flex gap-3 items-end max-w-3xl mx-auto">
            <textarea
              value={input}
              onChange={e => setInput(e.target.value)}
              onKeyDown={handleKeyDown}
              placeholder="Hỏi về luật thuế Việt Nam... (Enter để gửi, Shift+Enter xuống dòng)"
              rows={2}
              className="flex-1 border border-gray-300 rounded-xl px-4 py-3 text-sm resize-none focus:outline-none focus:ring-2 focus:border-transparent"
              style={{ '--tw-ring-color': '#028a39' } as React.CSSProperties}
            />
            <button
              onClick={() => sendMessage()}
              disabled={loading || !input.trim()}
              className="px-4 py-3 text-white rounded-xl font-medium text-sm disabled:opacity-50 transition-opacity hover:opacity-90 shrink-0 flex items-center gap-2"
              style={{ backgroundColor: '#028a39' }}
            >
              <Send className="w-4 h-4" />
              Gửi
            </button>
          </div>
          <p className="text-xs text-gray-400 text-center mt-2">
            Tư vấn mang tính tham khảo. Xác nhận với chuyên gia thuế cho trường hợp cụ thể.
          </p>
        </div>
      </div>
    </div>
  );
}
