import { useState, useRef, useEffect } from "react";
import { Button } from "./ui/button";
import { Input } from "./ui/input";
import { Brain, Send, Mic, Paperclip, Home, MessageSquare, LogOut, User, Menu, X, AlertCircle, Loader2 } from "lucide-react";
import { Link } from "react-router";
import { motion, AnimatePresence } from "motion/react";

const API_BASE_URL = import.meta.env.VITE_API_URL || "http://localhost:5000/api";

interface Message {
  id: number;
  text: string;
  sender: "user" | "bot";
  timestamp: string;
  intent?: string;
  source?: string;
  value?: any;
}

interface ChatHistory {
  id: number;
  title: string;
  timestamp: string;
}

export function ChatbotInterface() {
  // Student ID state
  const [studentId, setStudentId] = useState<number | null>(null);
  const [studentIdInput, setStudentIdInput] = useState("");
  const [showStudentIdModal, setShowStudentIdModal] = useState(true);
  const [studentIdError, setStudentIdError] = useState<string | null>(null);
  const [validatingStudentId, setValidatingStudentId] = useState(false);
  const [studentName, setStudentName] = useState<string | null>(null);

  const [messages, setMessages] = useState<Message[]>([
    {
      id: 1,
      text: "Hello! I'm your AI Placement Assistant. I can help you understand your profile data, placement chances, salary predictions, recommended companies, and skill assessments. What would you like to know?",
      sender: "bot",
      timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
    }
  ]);
  const [input, setInput] = useState("");
  const [isTyping, setIsTyping] = useState(false);
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [loadingResponse, setLoadingResponse] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const chatHistory: ChatHistory[] = [
    { id: 1, title: "Profile information check", timestamp: "2 hours ago" },
    { id: 2, title: "Placement probability", timestamp: "1 day ago" },
    { id: 3, title: "Salary predictions", timestamp: "2 days ago" },
    { id: 4, title: "Skill assessment", timestamp: "3 days ago" },
    { id: 5, title: "Company recommendations", timestamp: "5 days ago" },
  ];

  const suggestionChips = [
    "What is my CGPA?",
    "My placement probability?",
    "Predicted salary",
    "Recommended companies",
    "My DSA score",
    "Predicted job role"
  ];

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const validateStudentId = async () => {
    if (!studentIdInput.trim()) {
      setStudentIdError("Please enter a student ID");
      return;
    }

    setValidatingStudentId(true);
    setStudentIdError(null);

    try {
      const response = await fetch(`${API_BASE_URL}/student/${parseInt(studentIdInput)}`);
      const data = await response.json();

      if (response.ok) {
        setStudentId(parseInt(studentIdInput));
        setStudentName(data.name || data.student?.name || "Student");
        setShowStudentIdModal(false);
        console.log("[ChatBot] Student validated:", data.name || data.student?.name);
      } else {
        setStudentIdError(data.message || "Student ID not found");
      }
    } catch (error) {
      setStudentIdError("Error validating student ID. Please try again.");
      console.error("[ChatBot] Validation error:", error);
    } finally {
      setValidatingStudentId(false);
    }
  };

  const handleSend = async () => {
    if (!input.trim() || !studentId) return;

    const userMessage: Message = {
      id: messages.length + 1,
      text: input,
      sender: "user",
      timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
    };

    setMessages([...messages, userMessage]);
    setInput("");
    setIsTyping(true);
    setLoadingResponse(true);

    try {
      console.log(`[ChatBot] Sending message for student ${studentId}: ${userMessage.text}`);

      const response = await fetch(`${API_BASE_URL}/chatbot/message`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          student_id: studentId,
          message: userMessage.text
        })
      });

      const data = await response.json();
      console.log("[ChatBot] Response:", data);

      let botResponse = data.answer || "I couldn't process that request. Please try again.";

      // Format response with metadata if available
      if (data.source === 'student_profile') {
        botResponse += `\n\n📊 *Source: Your Student Profile*`;
      } else if (data.source === 'ml_predictions') {
        botResponse += `\n\n🤖 *Source: ML Predictions*`;
      } else if (data.source === 'company_data') {
        botResponse += `\n\n🏢 *Source: Company Database*`;
      }

      if (data.intent && data.intent !== 'no_match') {
        botResponse += `\n💡 *Query Type: ${data.intent.replace(/_/g, ' ').toUpperCase()}*`;
      }

      const botMessage: Message = {
        id: messages.length + 2,
        text: botResponse,
        sender: "bot",
        timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
        intent: data.intent,
        source: data.source,
        value: data.value
      };

      setMessages(prev => [...prev, botMessage]);
    } catch (error) {
      console.error("[ChatBot] Error:", error);

      const errorMessage: Message = {
        id: messages.length + 2,
        text: "I encountered an error while processing your request. Please try again.",
        sender: "bot",
        timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
      };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsTyping(false);
      setLoadingResponse(false);
    }
  };

  const handleSuggestionClick = (suggestion: string) => {
    setInput(suggestion);
  };

  const navItems = [
    { icon: Home, label: "Dashboard", path: "/dashboard" },
    { icon: MessageSquare, label: "Chatbot", path: "/chatbot", active: true },
  ];

  return (
    <>
      {/* Student ID Modal */}
      {showStudentIdModal && (
        <div className="fixed inset-0 bg-black/50 z-50 flex items-center justify-center p-4">
          <motion.div
            initial={{ scale: 0.95, opacity: 0 }}
            animate={{ scale: 1, opacity: 1 }}
            className="bg-card rounded-lg p-6 max-w-md w-full shadow-lg"
          >
            <div className="flex items-center gap-3 mb-4">
              <div className="w-10 h-10 bg-gradient-to-br from-[#003366] to-[#0055A4] rounded-lg flex items-center justify-center">
                <Brain className="w-6 h-6 text-white" />
              </div>
              <h2 className="text-xl" style={{ fontWeight: 600 }}>Welcome to Chatbot</h2>
            </div>

            <p className="text-sm text-muted-foreground mb-4">
              Please enter your student ID to access your personalized placement data and guidance.
            </p>

            <div className="space-y-4">
              <div>
                <label className="text-sm font-medium mb-2 block">Student ID</label>
                <Input
                  type="number"
                  placeholder="e.g., 200000"
                  value={studentIdInput}
                  onChange={(e) => {
                    setStudentIdInput(e.target.value);
                    setStudentIdError(null);
                  }}
                  onKeyPress={(e) => e.key === 'Enter' && validateStudentId()}
                  disabled={validatingStudentId}
                  className="h-10"
                />
                {studentIdError && (
                  <motion.div
                    initial={{ opacity: 0, y: -10 }}
                    animate={{ opacity: 1, y: 0 }}
                    className="mt-2 p-2 bg-destructive/10 border border-destructive/20 rounded text-sm text-destructive flex items-center gap-2"
                  >
                    <AlertCircle className="w-4 h-4" />
                    {studentIdError}
                  </motion.div>
                )}
              </div>

              <Button
                onClick={validateStudentId}
                disabled={!studentIdInput.trim() || validatingStudentId}
                className="w-full"
              >
                {validatingStudentId ? (
                  <>
                    <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                    Validating...
                  </>
                ) : (
                  'Start Chatting'
                )}
              </Button>
            </div>

            <p className="text-xs text-muted-foreground text-center mt-4">
              Your student ID is from your college admission email (e.g., 200001)
            </p>
          </motion.div>
        </div>
      )}

      {!showStudentIdModal && (
        <div className="h-screen bg-background flex overflow-hidden">
          {/* Left Sidebar - Chat History */}
          <aside className={`
            ${sidebarOpen ? 'translate-x-0' : '-translate-x-full'}
            lg:translate-x-0
            fixed lg:static inset-y-0 left-0 z-40
            w-64 bg-card border-r border-border
            transition-transform duration-300
            flex flex-col
          `}>
            {/* Sidebar Header */}
            <div className="p-4 border-b border-border flex items-center justify-between">
              <div className="flex items-center gap-2">
                <div className="w-8 h-8 bg-gradient-to-br from-[#003366] to-[#0055A4] rounded-lg flex items-center justify-center">
                  <Brain className="w-5 h-5 text-white" />
                </div>
                <h2 style={{ fontWeight: 600 }}>Chat History</h2>
              </div>
              <Button
                variant="ghost"
                size="icon"
                className="lg:hidden"
                onClick={() => setSidebarOpen(false)}
              >
                <X className="w-5 h-5" />
              </Button>
            </div>

            {/* New Chat Button */}
            <div className="p-4">
              <Button className="w-full bg-primary hover:bg-primary/90">
                <MessageSquare className="w-4 h-4 mr-2" />
                New Chat
              </Button>
            </div>

            {/* Chat History List */}
            <div className="flex-1 overflow-y-auto p-4 space-y-2">
              {chatHistory.map((chat) => (
                <button
                  key={chat.id}
                  className="w-full text-left p-3 rounded-lg hover:bg-muted transition-colors"
                >
                  <p className="text-sm truncate mb-1" style={{ fontWeight: 500 }}>
                    {chat.title}
                  </p>
                  <p className="text-xs text-muted-foreground">{chat.timestamp}</p>
                </button>
              ))}
            </div>

            {/* Navigation and Student Info */}
            <div className="p-4 border-t border-border space-y-3">
              <div className="bg-muted p-3 rounded-lg">
                <p className="text-xs text-muted-foreground">Current Student</p>
                <p className="text-sm font-medium">{studentName || `ID: ${studentId}`}</p>
              </div>

              {navItems.map((item) => (
                <Link key={item.label} to={item.path}>
                  <button
                    className={`w-full flex items-center gap-3 px-3 py-2 rounded-lg transition-colors ${
                      item.active
                        ? 'bg-primary text-primary-foreground'
                        : 'hover:bg-muted'
                    }`}
                  >
                    <item.icon className="w-4 h-4" />
                    <span className="text-sm">{item.label}</span>
                  </button>
                </Link>
              ))}
              <button className="w-full flex items-center gap-3 px-3 py-2 rounded-lg hover:bg-destructive/10 text-destructive transition-colors">
                <LogOut className="w-4 h-4" />
                <span className="text-sm">Logout</span>
              </button>
            </div>
          </aside>

          {/* Main Chat Area */}
          <div className="flex-1 flex flex-col">
            {/* Top Bar */}
            <header className="bg-card border-b border-border px-4 lg:px-6 py-4 flex items-center justify-between">
              <div className="flex items-center gap-4">
                <Button
                  variant="ghost"
                  size="icon"
                  className="lg:hidden"
                  onClick={() => setSidebarOpen(true)}
                >
                  <Menu className="w-5 h-5" />
                </Button>
                <div className="flex items-center gap-3">
                  <div className="w-10 h-10 bg-gradient-to-br from-[#003366] to-[#0055A4] rounded-full flex items-center justify-center">
                    <Brain className="w-6 h-6 text-white" />
                  </div>
                  <div>
                    <h1 style={{ fontWeight: 600 }}>Placement AI Assistant</h1>
                    <div className="flex items-center gap-2">
                      <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse"></div>
                      <p className="text-xs text-muted-foreground">Online</p>
                    </div>
                  </div>
                </div>
              </div>
              <Button variant="ghost" size="sm" onClick={() => setShowStudentIdModal(true)}>
                Change ID
              </Button>
            </header>

            {/* Messages Area */}
            <div className="flex-1 overflow-y-auto p-4 lg:p-6 space-y-4">
              <AnimatePresence>
                {messages.map((message, index) => (
                  <motion.div
                    key={message.id}
                    initial={{ opacity: 0, y: 10 }}
                    animate={{ opacity: 1, y: 0 }}
                    exit={{ opacity: 0 }}
                    transition={{ duration: 0.3 }}
                    className={`flex ${message.sender === 'user' ? 'justify-end' : 'justify-start'}`}
                  >
                    <div className={`flex gap-3 max-w-[85%] lg:max-w-[70%] ${message.sender === 'user' ? 'flex-row-reverse' : 'flex-row'}`}>
                      {/* Avatar */}
                      <div
                        className={`w-8 h-8 rounded-full flex items-center justify-center shrink-0 ${
                          message.sender === 'user'
                            ? 'bg-gradient-to-br from-[#003366] to-[#0055A4] text-white'
                            : 'bg-muted'
                        }`}
                      >
                        {message.sender === 'user' ? (
                          <User className="w-5 h-5" />
                        ) : (
                          <Brain className="w-5 h-5 text-primary" />
                        )}
                      </div>

                      {/* Message Bubble */}
                      <div className="space-y-1">
                        <div
                          className={`px-4 py-3 rounded-2xl ${
                            message.sender === 'user'
                              ? 'bg-primary text-primary-foreground'
                              : 'bg-muted'
                          }`}
                        >
                          <p className="whitespace-pre-line text-sm leading-relaxed">{message.text}</p>
                        </div>
                        <p
                          className={`text-xs text-muted-foreground px-2 ${
                            message.sender === 'user' ? 'text-right' : 'text-left'
                          }`}
                        >
                          {message.timestamp}
                        </p>
                      </div>
                    </div>
                  </motion.div>
                ))}
              </AnimatePresence>

              {/* Typing Indicator */}
              {isTyping && (
                <motion.div
                  initial={{ opacity: 0, y: 10 }}
                  animate={{ opacity: 1, y: 0 }}
                  className="flex justify-start"
                >
                  <div className="flex gap-3">
                    <div className="w-8 h-8 rounded-full bg-muted flex items-center justify-center shrink-0">
                      <Brain className="w-5 h-5 text-primary" />
                    </div>
                    <div className="px-4 py-3 rounded-2xl bg-muted">
                      <div className="flex gap-1">
                        <div
                          className="w-2 h-2 bg-muted-foreground rounded-full animate-bounce"
                          style={{ animationDelay: '0ms' }}
                        ></div>
                        <div
                          className="w-2 h-2 bg-muted-foreground rounded-full animate-bounce"
                          style={{ animationDelay: '150ms' }}
                        ></div>
                        <div
                          className="w-2 h-2 bg-muted-foreground rounded-full animate-bounce"
                          style={{ animationDelay: '300ms' }}
                        ></div>
                      </div>
                    </div>
                  </div>
                </motion.div>
              )}

              <div ref={messagesEndRef} />
            </div>

            {/* Suggestion Chips */}
            {messages.length <= 2 && (
              <div className="px-4 lg:px-6 pb-4">
                <div className="flex flex-wrap gap-2 justify-center">
                  {suggestionChips.map((chip) => (
                    <Button
                      key={chip}
                      variant="outline"
                      size="sm"
                      onClick={() => handleSuggestionClick(chip)}
                      className="rounded-full"
                    >
                      {chip}
                    </Button>
                  ))}
                </div>
              </div>
            )}

            {/* Input Area */}
            <div className="bg-card border-t border-border p-4 lg:p-6">
              <div className="max-w-4xl mx-auto">
                <div className="flex items-end gap-2">
                  <Button variant="ghost" size="icon" className="shrink-0">
                    <Paperclip className="w-5 h-5" />
                  </Button>

                  <div className="flex-1 relative">
                    <Input
                      value={input}
                      onChange={(e) => setInput(e.target.value)}
                      onKeyPress={(e) => e.key === 'Enter' && !loadingResponse && handleSend()}
                      placeholder="Ask about your profile, scores, placement chances..."
                      className="pr-12 h-12 rounded-xl resize-none"
                      disabled={loadingResponse}
                    />
                  </div>

                  <Button variant="ghost" size="icon" className="shrink-0">
                    <Mic className="w-5 h-5" />
                  </Button>

                  <Button
                    onClick={handleSend}
                    disabled={!input.trim() || loadingResponse}
                    size="icon"
                    className="shrink-0 w-12 h-12 bg-primary hover:bg-primary/90 rounded-xl"
                  >
                    {loadingResponse ? (
                      <Loader2 className="w-5 h-5 animate-spin" />
                    ) : (
                      <Send className="w-5 h-5" />
                    )}
                  </Button>
                </div>
                <p className="text-xs text-muted-foreground text-center mt-2">
                  AI can make mistakes. Verify important information with placement cell.
                </p>
              </div>
            </div>
          </div>

          {/* Overlay for mobile */}
          {sidebarOpen && (
            <div
              className="fixed inset-0 bg-black/50 z-30 lg:hidden"
              onClick={() => setSidebarOpen(false)}
            />
          )}
        </div>
      )}
    </>
  );
}
