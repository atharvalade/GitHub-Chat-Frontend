'use client';

import { useState, useRef, useEffect } from 'react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { ScrollArea } from '@/components/ui/scroll-area';
import { Card } from '@/components/ui/card';
import { Send, Sparkles } from 'lucide-react';
import { useAppStore } from '@/lib/store';
import { ChatMessage } from './chat-message';
import { SuggestedQuestions } from './suggested-questions';
import { EmptyState } from './empty-state';
import { sendChatMessage } from '@/lib/api';
import { toast } from 'sonner';

export function ChatArea() {
  const [input, setInput] = useState('');
  const [isTyping, setIsTyping] = useState(false);
  const scrollRef = useRef<HTMLDivElement>(null);
  const { messages, addMessage, isLoading, repository, chatHistory, setChatHistory } = useAppStore();

  useEffect(() => {
    // Auto-scroll to bottom when new messages arrive
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, [messages]);

  const handleSendMessage = async () => {
    if (!input.trim() || isTyping || !repository) return;

    const userMessage = {
      id: Date.now().toString(),
      role: 'user' as const,
      content: input.trim(),
      timestamp: new Date(),
    };

    addMessage(userMessage);
    const query = input.trim();
    setInput('');
    setIsTyping(true);

    try {
      // Call real backend API
      const response = await sendChatMessage(
        repository.owner,
        repository.name,
        query,
        chatHistory
      );

      const aiMessage = {
        id: (Date.now() + 1).toString(),
        role: 'assistant' as const,
        content: response.response,
        timestamp: new Date(),
      };
      
      addMessage(aiMessage);
      setChatHistory(response.history);
      setIsTyping(false);
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to get response';
      
      const errorAiMessage = {
        id: (Date.now() + 1).toString(),
        role: 'assistant' as const,
        content: `Sorry, I encountered an error: ${errorMessage}. Please try again.`,
        timestamp: new Date(),
      };
      
      addMessage(errorAiMessage);
      toast.error('Failed to get response', {
        description: errorMessage,
      });
      setIsTyping(false);
    }
  };

  const handleQuestionClick = (question: string) => {
    setInput(question);
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  if (isLoading) {
    return (
      <main className="flex-1 flex items-center justify-center bg-background">
        <Card className="p-8 max-w-md text-center space-y-4">
          <div className="flex justify-center">
            <div className="h-12 w-12 rounded-full bg-primary/10 flex items-center justify-center">
              <Sparkles className="h-6 w-6 text-primary animate-pulse" />
            </div>
          </div>
          <div>
            <h3 className="font-semibold text-lg mb-2">Analyzing Repository</h3>
            <p className="text-sm text-muted-foreground">
              Processing code structure, issues, and discussions...
            </p>
          </div>
        </Card>
      </main>
    );
  }

  return (
    <main className="flex-1 flex flex-col bg-background">
      {/* Messages Area */}
      <ScrollArea className="flex-1 px-4 md:px-6" ref={scrollRef}>
        <div className="max-w-4xl mx-auto py-6 space-y-6">
          {messages.length === 0 ? (
            <EmptyState repository={repository!} onQuestionClick={handleQuestionClick} />
          ) : (
            <>
              {messages.map((message) => (
                <ChatMessage key={message.id} message={message} />
              ))}
              {isTyping && (
                <div className="flex gap-3">
                  <div className="h-8 w-8 rounded-full bg-primary flex items-center justify-center flex-shrink-0">
                    <Sparkles className="h-4 w-4 text-primary-foreground" />
                  </div>
                  <Card className="flex-1 p-4 bg-muted/50">
                    <div className="flex gap-1">
                      <div className="h-2 w-2 rounded-full bg-muted-foreground animate-bounce" style={{ animationDelay: '0ms' }} />
                      <div className="h-2 w-2 rounded-full bg-muted-foreground animate-bounce" style={{ animationDelay: '150ms' }} />
                      <div className="h-2 w-2 rounded-full bg-muted-foreground animate-bounce" style={{ animationDelay: '300ms' }} />
                    </div>
                  </Card>
                </div>
              )}
            </>
          )}
        </div>
      </ScrollArea>

      {/* Suggested Questions (shown when no messages) */}
      {messages.length === 0 && !isLoading && (
        <div className="px-4 md:px-6 pb-4">
          <div className="max-w-4xl mx-auto">
            <SuggestedQuestions onQuestionClick={handleQuestionClick} />
          </div>
        </div>
      )}

      {/* Input Area */}
      <div className="border-t border-border/40 bg-background/95 backdrop-blur">
        <div className="max-w-4xl mx-auto px-4 md:px-6 py-4">
          <div className="flex gap-2">
            <Input
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyPress={handleKeyPress}
              placeholder="Ask anything about this repository..."
              className="flex-1"
              disabled={isTyping}
            />
            <Button
              onClick={handleSendMessage}
              disabled={!input.trim() || isTyping}
              size="icon"
              className="h-10 w-10"
            >
              <Send className="h-4 w-4" />
            </Button>
          </div>
          <p className="text-xs text-muted-foreground mt-2 text-center">
            Press Enter to send, Shift+Enter for new line
          </p>
        </div>
      </div>
    </main>
  );
}

