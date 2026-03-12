import { useEffect, useState } from "react";
import { Card } from "./ui/card";
import { Progress } from "./ui/progress";
import { Button } from "./ui/button";
import { Brain, ArrowLeft, TrendingUp, Target, Code, Briefcase, Trophy, CheckCircle2, Circle, Download, BarChart2, ChevronDown, ChevronUp } from "lucide-react";
import { Link } from "react-router";
import { motion } from "motion/react";

const API_BASE_URL = import.meta.env.VITE_API_URL || "http://localhost:5000/api";

interface Predictions {
  student_id: number;
  overall_placement_probability: number;
  predicted_salary_lpa: number;
  salary_range_min_lpa: number;
  salary_range_mid_lpa: number;
  salary_range_max_lpa: number;
  prob_salary_gt_2_lpa: number;
  prob_salary_gt_5_lpa: number;
  prob_salary_gt_10_lpa: number;
  prob_salary_gt_15_lpa: number;
  prob_salary_gt_20_lpa: number;
  prob_salary_gt_25_lpa: number;
  prob_salary_gt_30_lpa: number;
  prob_salary_gt_35_lpa: number;
  prob_salary_gt_40_lpa: number;
  predicted_job_role: string;
  recommended_companies: string;
}

export function PredictionResult() {
  const [predictions, setPredictions] = useState<Predictions | null>(null);
  const [loading, setLoading] = useState(true);
  const [expandedSalaries, setExpandedSalaries] = useState(false);
  const [studentsLoaded, setStudentsLoaded] = useState(false);

  useEffect(() => {
    // Try to get the stored student ID or get the latest prediction
    const fetchPredictions = async () => {
      try {
        // First try to get from localStorage
        const storedStudentId = localStorage.getItem('lastStudentId');
        
        if (storedStudentId) {
          const res = await fetch(`${API_BASE_URL}/predictions/${storedStudentId}`);
          const data = await res.json();
          if (data.predictions) {
            setPredictions(data.predictions);
            setStudentsLoaded(true);
          }
        } else {
          // Try student IDs in sequence to find latest prediction
          for (let i = 200099; i >= 200000; i--) {
            const res = await fetch(`${API_BASE_URL}/predictions/${i}`);
            const data = await res.json();
            if (data.predictions) {
              setPredictions(data.predictions);
              localStorage.setItem('lastStudentId', i.toString());
              setStudentsLoaded(true);
              break;
            }
          }
        }
      } catch (err) {
        console.error("Error fetching predictions:", err);
      } finally {
        setLoading(false);
      }
    };

    fetchPredictions();
  }, []);

  const companies = predictions?.recommended_companies 
    ? predictions.recommended_companies.split(',').map(c => c.trim()).filter(c => c)
    : [];

  const salaryThresholds = [
    { label: ">2 LPA", value: predictions?.prob_salary_gt_2_lpa || 0 },
    { label: ">5 LPA", value: predictions?.prob_salary_gt_5_lpa || 0 },
    { label: ">10 LPA", value: predictions?.prob_salary_gt_10_lpa || 0 },
    { label: ">15 LPA", value: predictions?.prob_salary_gt_15_lpa || 0 },
    { label: ">20 LPA", value: predictions?.prob_salary_gt_20_lpa || 0 },
    { label: ">25 LPA", value: predictions?.prob_salary_gt_25_lpa || 0 },
    { label: ">30 LPA", value: predictions?.prob_salary_gt_30_lpa || 0 },
    { label: ">35 LPA", value: predictions?.prob_salary_gt_35_lpa || 0 },
    { label: ">40 LPA", value: predictions?.prob_salary_gt_40_lpa || 0 },
  ];

  if (loading) {
    return (
      <div className="min-h-screen bg-background flex flex-col items-center justify-center">
        <div className="animate-spin mb-4">
          <div className="w-16 h-16 border-4 border-[#003366]/20 border-t-[#003366] rounded-full"></div>
        </div>
        <p className="text-lg font-medium">Loading predictions...</p>
      </div>
    );
  }

  if (!predictions || !studentsLoaded) {
    return (
      <div className="min-h-screen bg-background">
        <header className="bg-card border-b border-border px-6 py-4">
          <div className="max-w-7xl mx-auto flex items-center justify-between">
            <Link to="/dashboard">
              <Button variant="ghost">
                <ArrowLeft className="w-4 h-4 mr-2" />
                Back to Dashboard
              </Button>
            </Link>
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 bg-gradient-to-br from-[#003366] to-[#0055A4] rounded-xl flex items-center justify-center">
                <Brain className="w-6 h-6 text-white" />
              </div>
              <h1 className="text-xl" style={{ fontWeight: 700 }}>PlacementAI</h1>
            </div>
          </div>
        </header>

        <main className="max-w-7xl mx-auto px-6 py-12">
          <Card className="p-12 text-center">
            <div className="text-6xl mb-4">📊</div>
            <h2 className="text-2xl font-bold mb-2">No Predictions Yet</h2>
            <p className="text-muted-foreground mb-6">
              Start by generating your placement probability prediction to see your results here.
            </p>
            <Link to="/placement-probability">
              <Button className="bg-gradient-to-r from-[#003366] to-[#0055A4] hover:opacity-90 h-12 px-6">
                Generate Prediction
              </Button>
            </Link>
          </Card>
        </main>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-background from-50% to-[#003366]/3">
      {/* Header */}
      <header className="bg-card border-b border-border px-6 py-4 sticky top-0 z-50">
        <div className="max-w-7xl mx-auto flex items-center justify-between">
          <Link to="/dashboard">
            <Button variant="ghost">
              <ArrowLeft className="w-4 h-4 mr-2" />
              Back to Dashboard
            </Button>
          </Link>
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 bg-gradient-to-br from-[#003366] to-[#0055A4] rounded-xl flex items-center justify-center">
              <Brain className="w-6 h-6 text-white" />
            </div>
            <h1 className="text-xl" style={{ fontWeight: 700 }}>My Predictions</h1>
          </div>
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-6 py-12 space-y-12">
        {/* Top Section - Probability */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5 }}
        >
          <Card className="p-12 text-center bg-gradient-to-br from-[#003366] to-[#0055A4] text-white border-none shadow-xl">
            <div className="flex items-center justify-center gap-3 mb-4">
              <Trophy className="w-8 h-8 text-[#FFC107]" />
              <h2 className="text-2xl" style={{ fontWeight: 600 }}>Your Placement Probability</h2>
            </div>
            
            <div className="relative inline-block mb-6">
              <svg className="w-64 h-64" viewBox="0 0 200 200">
                <circle
                  cx="100"
                  cy="100"
                  r="80"
                  fill="none"
                  stroke="rgba(255,255,255,0.2)"
                  strokeWidth="16"
                />
                <circle
                  cx="100"
                  cy="100"
                  r="80"
                  fill="none"
                  stroke="#FFC107"
                  strokeWidth="16"
                  strokeLinecap="round"
                  strokeDasharray={`${(predictions.overall_placement_probability / 100) * 503.36} ${503.36}`}
                  transform="rotate(-90 100 100)"
                  className="transition-all duration-1000"
                />
              </svg>
              <div className="absolute inset-0 flex items-center justify-center">
                <div>
                  <div className="text-6xl mb-2" style={{ fontWeight: 700 }}>{predictions.overall_placement_probability}%</div>
                  <div className="text-sm text-white/80">
                    {predictions.overall_placement_probability >= 80 ? "High Probability" :
                     predictions.overall_placement_probability >= 60 ? "Good Probability" :
                     predictions.overall_placement_probability >= 40 ? "Moderate Probability" : "Low Probability"}
                  </div>
                </div>
              </div>
            </div>

            <p className="text-lg text-white/90 max-w-2xl mx-auto">
              Based on your technical skills, academic performance, and overall profile analysis, 
              this is your estimated chance of securing a placement.
            </p>
          </Card>
        </motion.div>

        {/* Salary Section */}
        <motion.section
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.5 }}
        >
          <div className="mb-6">
            <h2 className="text-3xl mb-2" style={{ fontWeight: 700 }}>💰 Salary Prediction</h2>
            <p className="text-muted-foreground">Expected salary and salary probability thresholds</p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
            <Card className="p-6 bg-gradient-to-br from-[#003366]/10 to-[#0055A4]/10 border-[#003366]/20">
              <p className="text-sm text-muted-foreground mb-2">Predicted Salary</p>
              <p className="text-4xl font-bold text-[#003366]">₹{predictions.predicted_salary_lpa} LPA</p>
            </Card>

            <Card className="p-6 bg-gradient-to-br from-[#10B981]/10 to-[#059669]/10 border-[#10B981]/20">
              <p className="text-sm text-muted-foreground mb-2">Salary Range</p>
              <p className="text-lg font-bold text-[#10B981]">
                ₹{predictions.salary_range_min_lpa} - ₹{predictions.salary_range_max_lpa} LPA
              </p>
              <p className="text-xs text-muted-foreground mt-1">Min to Max Range</p>
            </Card>

            <Card className="p-6 bg-gradient-to-br from-[#FFC107]/10 to-[#F59E0B]/10 border-[#FFC107]/20">
              <p className="text-sm text-muted-foreground mb-2">Mid Range</p>
              <p className="text-2xl font-bold text-[#FFC107]">₹{predictions.salary_range_mid_lpa} LPA</p>
            </Card>
          </div>

          {/* Salary Thresholds */}
          <Card className="p-6">
            <button 
              onClick={() => setExpandedSalaries(!expandedSalaries)}
              className="w-full flex items-center justify-between mb-4 hover:opacity-80 transition-opacity"
            >
              <h3 className="text-lg font-bold flex items-center gap-2">
                <BarChart2 className="w-5 h-5" />
                Cumulative Salary Probabilities
              </h3>
              {expandedSalaries ? <ChevronUp className="w-5 h-5" /> : <ChevronDown className="w-5 h-5" />}
            </button>

            {expandedSalaries && (
              <motion.div
                initial={{ opacity: 0, height: 0 }}
                animate={{ opacity: 1, height: "auto" }}
                exit={{ opacity: 0, height: 0 }}
                className="space-y-4"
              >
                {salaryThresholds.map((threshold, index) => (
                  <motion.div
                    key={threshold.label}
                    initial={{ opacity: 0, x: -20 }}
                    animate={{ opacity: 1, x: 0 }}
                    transition={{ delay: index * 0.05 }}
                  >
                    <div className="flex items-center justify-between mb-2">
                      <span className="font-medium">{threshold.label}</span>
                      <span className="text-sm font-bold text-[#003366]">{threshold.value}%</span>
                    </div>
                    <div className="w-full h-3 bg-muted rounded-full overflow-hidden">
                      <motion.div
                        initial={{ width: 0 }}
                        animate={{ width: `${threshold.value}%` }}
                        transition={{ delay: index * 0.1 + 0.2, duration: 0.8 }}
                        className="h-full bg-gradient-to-r from-[#003366] to-[#0055A4]"
                      />
                    </div>
                  </motion.div>
                ))}
              </motion.div>
            )}
          </Card>
        </motion.section>

        {/* Job Role Section */}
        <motion.section
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.5 }}
        >
          <div className="mb-6">
            <h2 className="text-3xl mb-2" style={{ fontWeight: 700 }}>🎯 Predicted Job Role</h2>
          </div>

          <Card className="p-8 bg-gradient-to-br from-[#FFC107]/10 to-[#F59E0B]/10 border-[#FFC107]/20 text-center">
            <div className="text-6xl mb-4">💼</div>
            <h3 className="text-3xl font-bold text-[#FFC107] mb-2">{predictions.predicted_job_role}</h3>
            <p className="text-muted-foreground">Based on your skills and profile</p>
          </Card>
        </motion.section>

        {/* Recommended Companies Section */}
        <motion.section
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.5 }}
        >
          <div className="mb-6">
            <h2 className="text-3xl mb-2" style={{ fontWeight: 700 }}>🏢 Recommended Companies</h2>
            <p className="text-muted-foreground">Best-fit companies based on your profile</p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {companies.map((company, index) => (
              <motion.div
                key={company}
                initial={{ opacity: 0, scale: 0.9 }}
                whileInView={{ opacity: 1, scale: 1 }}
                viewport={{ once: true }}
                transition={{ delay: index * 0.1 }}
              >
                <Card className="p-6 hover:shadow-lg transition-shadow border-[#003366]/20 bg-gradient-to-br from-[#003366]/5 to-[#0055A4]/5">
                  <div className="flex items-center gap-3 mb-2">
                    <div className="w-8 h-8 bg-gradient-to-br from-[#003366] to-[#0055A4] rounded-lg flex items-center justify-center text-white text-xs font-bold">
                      {company.charAt(0)}
                    </div>
                    <h3 className="font-bold text-lg">{company}</h3>
                  </div>
                  <p className="text-sm text-muted-foreground">Recommended match</p>
                </Card>
              </motion.div>
            ))}
          </div>
        </motion.section>

        {/* Action Buttons */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.5 }}
          className="flex gap-4 pt-8 pb-12"
        >
          <Link to="/placement-probability" className="flex-1">
            <Button className="w-full h-12 bg-gradient-to-r from-[#003366] to-[#0055A4] hover:opacity-90">
              <TrendingUp className="w-4 h-4 mr-2" />
              Generate New Prediction
            </Button>
          </Link>
          <Button variant="outline" className="h-12 px-6">
            <Download className="w-4 h-4 mr-2" />
            Download Report
          </Button>
        </motion.div>
      </main>
    </div>
  );
}
