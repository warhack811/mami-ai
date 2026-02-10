"use client";

import { useState, useRef, useEffect } from 'react';
import { Send, FileCode, Search, User, Bot, AlertTriangle, Terminal, Mic, Square } from 'lucide-react';
import ReactMarkdown from 'react-markdown';
import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter';
import { atomDark } from 'react-syntax-highlighter/dist/esm/styles/prism';
import api from '@/lib/api';

interface Message {
  role: 'user' | 'assistant';
  content: string;
}

export default function ChatInterface() {
  const [input, setInput] = useState('');
  const [messages, setMessages] = useState<Message[]>([
    { role: 'assistant', content: "Hello! I'm Mami AI. How can I help you today?" }
  ]);
  const [isLoading, setIsLoading] = useState(false);
  const [isRecording, setIsRecording] = useState(false);
  const [artifact, setArtifact] = useState<string | null>(null);
  const mediaRecorderRef = useRef<MediaRecorder | null>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(scrollToBottom, [messages]);

  const startRecording = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      const mediaRecorder = new MediaRecorder(stream);
      mediaRecorderRef.current = mediaRecorder;
      const chunks: Blob[] = [];

      mediaRecorder.ondataavailable = (e) => chunks.push(e.data);
      mediaRecorder.onstop = async () => {
        const blob = new Blob(chunks, { type: 'audio/webm' });
        const formData = new FormData();
        formData.append('file', blob, 'recording.webm');

        setIsLoading(true);
        try {
          const res = await api.post('/voice/transcribe', formData);
          setInput(res.data.text);
        } catch (err) {
          console.error("Transcription failed", err);
        } finally {
          setIsLoading(false);
        }
      };

      mediaRecorder.start();
      setIsRecording(true);
    } catch (err) {
      console.error("Microphone access denied", err);
    }
  };

  const stopRecording = () => {
    mediaRecorderRef.current?.stop();
    setIsRecording(false);
  };

  const sendMessage = async () => {
    if (!input.trim()) return;

    const userMessage: Message = { role: 'user', content: input };
    setMessages(prev => [...prev, userMessage]);
    setInput('');
    setIsLoading(true);

    try {
      // Use SSE for streaming
      const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1'}/chat/chat/stream?message=${encodeURIComponent(input)}`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
      });

      if (!response.body) throw new Error("No response body");

      const reader = response.body.getReader();
      const decoder = new TextDecoder();
      let assistantMessage = { role: 'assistant', content: '' };

      setMessages(prev => [...prev, assistantMessage as Message]);

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        const chunk = decoder.decode(value);
        const lines = chunk.split('\n');

        for (const line of lines) {
          if (line.startsWith('data: ')) {
            const dataStr = line.slice(6);
            if (dataStr === '[DONE]') break;

            try {
              const data = JSON.parse(dataStr);
              if (data.type === 'token') {
                assistantMessage.content += data.content;
                setMessages(prev => {
                  const newMessages = [...prev];
                  newMessages[newMessages.length - 1] = { ...assistantMessage } as Message;
                  return newMessages;
                });

                // Check for code blocks to update Artifact
                if (assistantMessage.content.includes('```')) {
                   const match = assistantMessage.content.match(/```(\w+)?\n([\s\S]*?)```/);
                   if (match) {
                     setArtifact(match[2]);
                   }
                }

              } else if (data.type === 'tool_start') {
                 // Show tool indicator
                 console.log("Tool started:", data.tool);
              }
            } catch (e) {
              console.error("Error parsing SSE data", e);
            }
          }
        }
      }

    } catch (error) {
      console.error('Error sending message:', error);
      setMessages(prev => [...prev, {
        role: 'assistant',
        content: "I'm having trouble connecting to my brain. Please try again later."
      }]);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="flex h-screen bg-gray-900 text-gray-100 overflow-hidden">
      {/* Main Chat Area */}
      <div className={`flex flex-col flex-1 ${artifact ? 'w-2/3' : 'w-full'} transition-all duration-300`}>
        {/* Header */}
        <header className="flex items-center justify-between p-4 border-b border-gray-800 bg-gray-900/50 backdrop-blur-md sticky top-0 z-10">
            <h1 className="text-xl font-bold bg-gradient-to-r from-blue-400 to-purple-500 bg-clip-text text-transparent">Mami AI</h1>
            <div className="flex space-x-4">
                <span className="text-xs px-2 py-1 rounded bg-green-500/20 text-green-400 border border-green-500/30">Online</span>
            </div>
        </header>

        {/* Messages */}
        <div className="flex-1 overflow-y-auto p-4 space-y-4">
            {messages.map((msg, idx) => (
            <div key={idx} className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}>
                <div className={`max-w-[85%] rounded-lg p-3 ${
                msg.role === 'user'
                    ? 'bg-blue-600 text-white rounded-br-none'
                    : 'bg-gray-800 text-gray-200 rounded-bl-none border border-gray-700'
                }`}>
                <div className="flex items-center mb-1 text-xs opacity-50">
                    {msg.role === 'assistant' ? <Bot size={12} className="mr-1" /> : <User size={12} className="mr-1" />}
                    <span>{msg.role === 'user' ? 'You' : 'Mami AI'}</span>
                </div>
                <div className="prose prose-invert text-sm">
                    <ReactMarkdown
                        components={{
                            code({node, inline, className, children, ...props}) {
                                const match = /language-(\w+)/.exec(className || '')
                                return !inline && match ? (
                                <SyntaxHighlighter
                                    {...props}
                                    style={atomDark}
                                    language={match[1]}
                                    PreTag="div"
                                >
                                    {String(children).replace(/\n$/, '')}
                                </SyntaxHighlighter>
                                ) : (
                                <code {...props} className={className}>
                                    {children}
                                </code>
                                )
                            }
                        }}
                    >
                        {msg.content}
                    </ReactMarkdown>
                </div>
                </div>
            </div>
            ))}
            {isLoading && (
            <div className="flex justify-start">
                <div className="bg-gray-800 rounded-lg p-3 rounded-bl-none border border-gray-700">
                <span className="animate-pulse">Thinking...</span>
                </div>
            </div>
            )}
            <div ref={messagesEndRef} />
        </div>

        {/* Input */}
        <div className="p-4 border-t border-gray-800 bg-gray-900">
            <div className="flex items-center space-x-2">
          <button
            onClick={isRecording ? stopRecording : startRecording}
            className={`p-3 rounded-full transition-colors ${isRecording ? 'bg-red-600 hover:bg-red-500 animate-pulse' : 'bg-gray-700 hover:bg-gray-600'}`}
          >
            {isRecording ? <Square size={20} /> : <Mic size={20} />}
          </button>
            <input
                type="text"
                value={input}
                onChange={(e) => setInput(e.target.value)}
                onKeyDown={(e) => e.key === 'Enter' && sendMessage()}
            placeholder={isRecording ? "Listening..." : "Ask anything..."}
                className="flex-1 bg-gray-800 border-none rounded-full px-4 py-3 focus:ring-2 focus:ring-blue-500 outline-none text-white placeholder-gray-500"
            disabled={isLoading || isRecording}
            />
            <button
                onClick={sendMessage}
                disabled={isLoading || !input.trim()}
                className="p-3 bg-blue-600 rounded-full hover:bg-blue-500 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
            >
                <Send size={20} />
            </button>
            </div>
        </div>
      </div>

      {/* Artifact Panel */}
      {artifact && (
        <div className="w-1/3 border-l border-gray-800 bg-gray-950 flex flex-col transition-all duration-300">
            <div className="p-4 border-b border-gray-800 flex justify-between items-center">
                <h2 className="text-sm font-semibold flex items-center">
                    <Terminal size={16} className="mr-2" />
                    Artifact / Code
                </h2>
                <button onClick={() => setArtifact(null)} className="text-gray-500 hover:text-white">x</button>
            </div>
            <div className="flex-1 overflow-auto p-4">
                <SyntaxHighlighter
                    style={atomDark}
                    language="python" // Default or auto-detect
                    showLineNumbers={true}
                    wrapLines={true}
                >
                    {artifact}
                </SyntaxHighlighter>
            </div>
        </div>
      )}
    </div>
  );
}
