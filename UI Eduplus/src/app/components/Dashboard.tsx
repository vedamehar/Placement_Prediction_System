import { useState } from "react";
import { Button } from "./ui/button";
import { Card } from "./ui/card";
import { Progress } from "./ui/progress";
import { Brain, Bell, User, LogOut, MessageSquare, BarChart3, FileText, TrendingUp, Home, Target, Building2, Calendar, Clock, ChevronRight, Zap } from "lucide-react";
import { Link } from "react-router";
import { motion } from "motion/react";

export function Dashboard() {
  const [sidebarOpen, setSidebarOpen] = useState(true);

  const stats = [
    { 
      label: "Placement Probability", 
      value: 82, 
      icon: Target,
      color: "from-[#003366] to-[#0055A4]",
      suffix: "%"
    },
    { 
      label: "Interview Readiness", 
      value: 75, 
      icon: TrendingUp,
      color: "from-[#10B981] to-[#059669]",
      suffix: "%"
    },
    { 
      label: "Eligible Companies", 
      value: 47, 
      icon: Building2,
      color: "from-[#FFC107] to-[#F59E0B]",
      suffix: ""
    },
    { 
      label: "Skill Completion", 
      value: 68, 
      icon: BarChart3,
      color: "from-[#8B5CF6] to-[#7C3AED]",
      suffix: "%"
    },
  ];

  const recentChats = [
    { id: 1, question: "What are my placement chances?", time: "2 hours ago", result: "82%" },
    { id: 2, question: "Top companies for 8 CGPA", time: "1 day ago", result: "12 companies" },
    { id: 3, question: "Skill gap analysis", time: "2 days ago", result: "DSA needed" },
  ];

  const upcomingCompanies = [
    { name: "Google", role: "SDE", package: "₹42 LPA", deadline: "Mar 5", logo: "🔵" },
    { name: "Microsoft", role: "SDE-1", package: "₹35 LPA", deadline: "Mar 8", logo: "🟦" },
    { name: "Amazon", role: "SDE Intern", package: "₹28 LPA", deadline: "Mar 12", logo: "🟧" },
    { name: "Accenture", role: "Associate", package: "₹6 LPA", deadline: "Mar 15", logo: "🟪" },
  ];

  const navItems = [
    { icon: Home, label: "Dashboard", path: "/dashboard", active: true },
    { icon: Zap, label: "Placement Probability", path: "/placement-probability" },
    { icon: MessageSquare, label: "Chatbot", path: "/chatbot" },
    { icon: FileText, label: "My Predictions", path: "/predictions" },
  ];

  return (
    <div className="min-h-screen bg-background flex">
      {/* Sidebar */}
      <aside className={`${sidebarOpen ? 'w-64' : 'w-20'} bg-card border-r border-border transition-all duration-300 hidden lg:flex flex-col`}>
        <div className="p-6 border-b border-border">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 bg-gradient-to-br from-[#003366] to-[#0055A4] rounded-xl flex items-center justify-center shrink-0">
              <Brain className="w-6 h-6 text-white" />
            </div>
            {sidebarOpen && (
              <div>
                <h1 className="text-lg" style={{ fontWeight: 700 }}>PlacementAI</h1>
                <p className="text-xs text-muted-foreground">Student Portal</p>
              </div>
            )}
          </div>
        </div>

        <nav className="flex-1 p-4 space-y-2">
          {navItems.map((item) => (
            <Link key={item.label} to={item.path}>
              <button
                className={`w-full flex items-center gap-3 px-4 py-3 rounded-lg transition-colors ${
                  item.active 
                    ? 'bg-primary text-primary-foreground' 
                    : 'hover:bg-muted text-foreground'
                }`}
              >
                <item.icon className="w-5 h-5 shrink-0" />
                {sidebarOpen && <span>{item.label}</span>}
              </button>
            </Link>
          ))}
        </nav>

        <div className="p-4 border-t border-border">
          <button className="w-full flex items-center gap-3 px-4 py-3 rounded-lg hover:bg-destructive/10 text-destructive transition-colors">
            <LogOut className="w-5 h-5 shrink-0" />
            {sidebarOpen && <span>Logout</span>}
          </button>
        </div>
      </aside>

      {/* Main Content */}
      <div className="flex-1 flex flex-col">
        {/* Top Navbar */}
        <header className="bg-card border-b border-border px-6 py-4">
          <div className="flex items-center justify-between">
            <div>
              <h2 className="text-2xl" style={{ fontWeight: 700 }}>Dashboard</h2>
              <p className="text-sm text-muted-foreground">Welcome back, Aum 👋</p>
            </div>
            <div className="flex items-center gap-4">
              <Button variant="ghost" size="icon" className="relative">
                <Bell className="w-5 h-5" />
                <span className="absolute top-2 right-2 w-2 h-2 bg-destructive rounded-full"></span>
              </Button>
              <div className="flex items-center gap-3">
                <div className="w-10 h-10 bg-gradient-to-br from-[#003366] to-[#0055A4] rounded-full flex items-center justify-center text-white">
                  A
                </div>
              </div>
            </div>
          </div>
        </header>

        {/* Dashboard Content */}
        <main className="flex-1 overflow-auto p-6">
          {/* Stats Grid */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
            {stats.map((stat, index) => (
              <motion.div
                key={stat.label}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: index * 0.1 }}
              >
                <Card className="p-6 hover:shadow-lg transition-shadow duration-300">
                  <div className="flex items-start justify-between mb-4">
                    <div className={`w-12 h-12 bg-gradient-to-br ${stat.color} rounded-xl flex items-center justify-center`}>
                      <stat.icon className="w-6 h-6 text-white" />
                    </div>
                  </div>
                  <div className="space-y-2">
                    <p className="text-sm text-muted-foreground">{stat.label}</p>
                    <p className="text-3xl" style={{ fontWeight: 700 }}>
                      {stat.value}{stat.suffix}
                    </p>
                    {stat.suffix === "%" && (
                      <Progress value={stat.value} className="h-2" />
                    )}
                  </div>
                </Card>
              </motion.div>
            ))}
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {/* Recent Chat History */}
            <Card className="p-6">
              <div className="flex items-center justify-between mb-6">
                <div>
                  <h3 className="text-xl" style={{ fontWeight: 600 }}>Recent Chat History</h3>
                  <p className="text-sm text-muted-foreground">Your latest AI conversations</p>
                </div>
                <Link to="/chatbot">
                  <Button variant="ghost" size="sm">
                    View All
                    <ChevronRight className="w-4 h-4 ml-1" />
                  </Button>
                </Link>
              </div>
              <div className="space-y-4">
                {recentChats.map((chat) => (
                  <div key={chat.id} className="flex items-start gap-4 p-4 rounded-lg hover:bg-muted/50 transition-colors cursor-pointer">
                    <div className="w-10 h-10 bg-gradient-to-br from-[#003366] to-[#0055A4] rounded-lg flex items-center justify-center shrink-0">
                      <MessageSquare className="w-5 h-5 text-white" />
                    </div>
                    <div className="flex-1 min-w-0">
                      <p className="truncate mb-1" style={{ fontWeight: 500 }}>{chat.question}</p>
                      <div className="flex items-center gap-2 text-sm text-muted-foreground">
                        <Clock className="w-3 h-3" />
                        <span>{chat.time}</span>
                        <span>•</span>
                        <span className="text-primary">{chat.result}</span>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </Card>

            {/* Upcoming Companies */}
            <Card className="p-6">
              <div className="flex items-center justify-between mb-6">
                <div>
                  <h3 className="text-xl" style={{ fontWeight: 600 }}>Upcoming Companies</h3>
                  <p className="text-sm text-muted-foreground">Companies visiting campus</p>
                </div>
                <Button variant="ghost" size="sm">
                  View All
                  <ChevronRight className="w-4 h-4 ml-1" />
                </Button>
              </div>
              <div className="space-y-3">
                {upcomingCompanies.map((company, index) => (
                  <div key={index} className="flex items-center justify-between p-4 rounded-lg border border-border hover:border-primary/50 transition-colors">
                    <div className="flex items-center gap-3">
                      <div className="text-2xl">{company.logo}</div>
                      <div>
                        <p style={{ fontWeight: 600 }}>{company.name}</p>
                        <p className="text-sm text-muted-foreground">{company.role}</p>
                      </div>
                    </div>
                    <div className="text-right">
                      <p className="text-sm" style={{ fontWeight: 600, color: '#10B981' }}>{company.package}</p>
                      <div className="flex items-center gap-1 text-xs text-muted-foreground">
                        <Calendar className="w-3 h-3" />
                        <span>{company.deadline}</span>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </Card>
          </div>
        </main>
      </div>
    </div>
  );
}