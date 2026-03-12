import { useState, useEffect } from "react";
import { Button } from "./ui/button";
import { Card } from "./ui/card";
import { Input } from "./ui/input";
import { Textarea } from "./ui/textarea";
import { Brain, ArrowLeft, Loader2, CheckCircle2, AlertCircle, ExternalLink } from "lucide-react";
import { Link } from "react-router";
import { motion } from "motion/react";

const API_BASE_URL = import.meta.env.VITE_API_URL || "http://localhost:5000/api";

interface StudentData {
  studentId: number;
  name: string;
}

interface FormData {
  dsa_score: number | null;
  project_score: number | null;
  aptitude_score: number | null;
  hr_score: number | null;
  resume_ats_score: number | null;
  github_projects: number;
  github_project_links: string[];
}

interface HRQuestion {
  id: number;
  text: string;
  answer: string;
}

export function PlacementProbability() {
  const [step, setStep] = useState(0);
  const [student, setStudent] = useState<StudentData | null>(null);
  const [studentId, setStudentId] = useState("");
  const [formData, setFormData] = useState<FormData>({
    dsa_score: null,
    project_score: null,
    aptitude_score: null,
    hr_score: null,
    resume_ats_score: null,
    github_projects: 0,
    github_project_links: []
  });

  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  
  // LeetCode
  const [leetcodeUsername, setLeetcodeUsername] = useState("");
  const [fetchingLeetcode, setFetchingLeetcode] = useState(false);

  // GitHub
  const [githubRepoLinks, setGithubRepoLinks] = useState<string[]>([]);
  const [currentRepoInput, setCurrentRepoInput] = useState("");
  const [analyzingGithub, setAnalyzingGithub] = useState(false);
  const [githubReport, setGithubReport] = useState<any>(null);

  // Aptitude & ATS
  const [aptitudeAtsInfo, setAptitudeAtsInfo] = useState<any>(null);

  // HR Round
  const [hrQuestions, setHrQuestions] = useState<HRQuestion[]>([]);
  const [evaluatingHR, setEvaluatingHR] = useState(false);

  const [predictions, setPredictions] = useState(null);

  const steps = [
    { title: "Validate Student", subtitle: "Enter your student ID" },
    { title: "DSA Score", subtitle: "From LeetCode or manual entry" },
    { title: "GitHub Projects", subtitle: "Analyze GitHub repository links" },
    { title: "Aptitude Score", subtitle: "Take test and enter score" },
    { title: "Resume ATS", subtitle: "Check ATS score and enter" },
    { title: "HR Round", subtitle: "Answer interview questions" },
    { title: "Generating", subtitle: "ML predictions in progress..." }
  ];

  // Load aptitude/ATS info on mount
  useEffect(() => {
    const loadAptitudeAtsInfo = async () => {
      try {
        const res = await fetch(`${API_BASE_URL}/aptitude/links`);
        const data = await res.json();
        setAptitudeAtsInfo(data);
        console.log("[Aptitude/ATS] Links loaded");
      } catch (err) {
        console.log("[PlacementProbability] Could not load aptitude/ATS info");
      }
    };
    loadAptitudeAtsInfo();
  }, []);

  // Load HR questions on mount
  useEffect(() => {
    const loadHRQuestions = async () => {
      try {
        console.log("[HR Questions] Fetching from", `${API_BASE_URL}/hr-round/questions`);
        const res = await fetch(`${API_BASE_URL}/hr-round/questions`);
        const data = await res.json();
        console.log("[HR Questions] Response received:", data);
        const questions: HRQuestion[] = data.questions.map((q: string, idx: number) => ({
          id: idx,
          text: q,
          answer: ""
        }));
        setHrQuestions(questions);
        console.log("[HR Questions] Loaded", questions.length, "questions");
      } catch (err) {
        console.error("[PlacementProbability] Error loading HR questions:", err);
      }
    };
    loadHRQuestions();
  }, []);

  const validateStudent = async () => {
    if (!studentId.trim()) {
      setError("Please enter a student ID");
      return;
    }
    
    setLoading(true);
    setError(null);
    
    try {
      const res = await fetch(`${API_BASE_URL}/student/${studentId}`);
      const data = await res.json();
      
      if (data.exists && data.name) {
        setStudent({ studentId: parseInt(studentId), name: data.name });
        setStep(1);
        setError(null);
      } else if (!data.exists) {
        setError("Student not found. Please check your ID. Valid IDs: 200000-200099");
      } else {
        setError("Failed to validate student. Please try again.");
      }
    } catch (err) {
      setError(`Error validating student: ${err instanceof Error ? err.message : "Unknown error"}`);
    } finally {
      setLoading(false);
    }
  };

  const fetchLeetcodeScore = async () => {
    if (!leetcodeUsername.trim()) {
      setError("Please enter a LeetCode username");
      return;
    }
    
    setFetchingLeetcode(true);
    setError(null);
    
    try {
      const res = await fetch(`${API_BASE_URL}/integrations/leetcode`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ username: leetcodeUsername })
      });
      const data = await res.json();
      
      if (data.score !== null && data.score !== undefined && typeof data.score === 'number') {
        setFormData(prev => ({ ...prev, dsa_score: data.score }));
        setLeetcodeUsername("");
        setError(null);
      } else {
        const errorMsg = data.error || "Username not found. Please enter score manually.";
        setError(errorMsg);
      }
    } catch (err) {
      setError("Error fetching LeetCode data. Please try again or enter manually.");
    } finally {
      setFetchingLeetcode(false);
    }
  };

  const addGithubRepo = () => {
    if (!currentRepoInput.trim()) {
      setError("Please enter a repository link");
      return;
    }
    
    if (!currentRepoInput.includes("github.com")) {
      setError("Please enter a valid GitHub repository URL");
      return;
    }
    
    const newLinks = [...githubRepoLinks, currentRepoInput];
    setGithubRepoLinks(newLinks);
    setCurrentRepoInput("");
    setError(null);
  };

  const removeGithubRepo = (index: number) => {
    const newLinks = githubRepoLinks.filter((_, i) => i !== index);
    setGithubRepoLinks(newLinks);
  };

  const analyzeGithubProjects = async () => {
    if (!githubRepoLinks || githubRepoLinks.length === 0) {
      setError("Please add at least one GitHub repository link");
      return;
    }
    
    setAnalyzingGithub(true);
    setError(null);
    
    try {
      console.log("[GitHub] Analyzing", githubRepoLinks.length, "repositories");
      const res = await fetch(`${API_BASE_URL}/integrations/github-projects`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ repo_urls: githubRepoLinks })
      });
      
      const data = await res.json();
      
      if (data.score !== null && typeof data.score === 'number') {
        console.log("[GitHub] Score received:", data.score);
        setFormData(prev => ({ 
          ...prev, 
          project_score: data.score,
          github_projects: githubRepoLinks.length,
          github_project_links: githubRepoLinks
        }));
        setGithubReport(data);
        setError(null);
      } else {
        setError(data.error || "Failed to analyze repositories");
      }
    } catch (err) {
      console.error("[GitHub] Error:", err);
      setError("Error analyzing GitHub projects. Please try again or enter manually.");
    } finally {
      setAnalyzingGithub(false);
    }
  };

  const openLink = (url: string) => {
    window.open(url, '_blank');
  };

  const updateHRAnswer = (id: number, answer: string) => {
    setHrQuestions(prev => 
      prev.map(q => q.id === id ? { ...q, answer } : q)
    );
  };

  const evaluateHRRound = async () => {
    // Check if all questions are answered
    const unanswered = hrQuestions.filter(q => !q.answer.trim());
    if (unanswered.length > 0) {
      setError(`Please answer all ${unanswered.length} question(s)`);
      return;
    }

    setEvaluatingHR(true);
    setError(null);

    try {
      const res = await fetch(`${API_BASE_URL}/hr-round/evaluate`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ answers: hrQuestions.map(q => q.answer) })
      });

      const data = await res.json();

      if (data.score !== null && typeof data.score === 'number') {
        console.log("[HR Round] Score received:", data.score);
        setFormData(prev => ({ ...prev, hr_score: data.score }));
        setError(null);
      } else {
        setError(data.error || "Failed to evaluate HR responses");
      }
    } catch (err) {
      console.error("[HR Round] Error:", err);
      setError("Error evaluating HR round. Please try again.");
    } finally {
      setEvaluatingHR(false);
    }
  };

  const generatePredictions = async () => {
    if (!student) return;
    
    // Validation - only 5 required scores
    if (formData.dsa_score === null || formData.project_score === null || 
        formData.aptitude_score === null ||
        formData.hr_score === null || formData.resume_ats_score === null) {
      setError("Please fill all required fields");
      return;
    }

    setStep(6);
    setLoading(true);
    setError(null);

    try {
      const res = await fetch(`${API_BASE_URL}/predictions/generate`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          studentId: student.studentId,
          dsa_score: formData.dsa_score,
          project_score: formData.project_score,
          aptitude_score: formData.aptitude_score,
          hr_score: formData.hr_score,
          resume_ats_score: formData.resume_ats_score,
          github_projects: formData.github_projects,
          github_project_links: githubRepoLinks
        })
      });

      if (!res.ok) throw new Error("Failed to generate predictions");
      
      const data = await res.json();
      
      // Save predictions
      await fetch(`${API_BASE_URL}/predictions/save`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          studentId: student.studentId,
          predictions: data
        })
      });
      
      localStorage.setItem('lastStudentId', student.studentId.toString());
      
      setPredictions(data);
      setStep(7); // Show results
    } catch (err) {
      setError("Error generating predictions. Please try again.");
      setStep(5);
    } finally {
      setLoading(false);
    }
  };

  const goBack = () => {
    if (step > 0) setStep(step - 1);
  };

  const goNext = () => {
    setError(null);
    
    if (step === 0) {
      validateStudent();
    } else if (step === 1 && formData.dsa_score === null) {
      setError("Please enter DSA score");
    } else if (step === 2 && formData.project_score === null) {
      setError("Please enter project score");
    } else if (step === 3 && formData.aptitude_score === null) {
      setError("Please enter aptitude score");
    } else if (step === 4 && formData.resume_ats_score === null) {
      setError("Please enter resume ATS score");
    } else if (step === 5 && formData.hr_score === null) {
      setError("Please complete HR round evaluation");
    } else if (step === 5) {
      generatePredictions();
    } else {
      setStep(step + 1);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-[#003366]/5 via-background to-[#0055A4]/5">
      {/* Header */}
      <div className="bg-card border-b border-border">
        <div className="max-w-4xl mx-auto px-6 py-6">
          <Link to="/" className="flex items-center gap-2 text-primary hover:text-primary/80 mb-4 w-fit">
            <ArrowLeft className="w-4 h-4" />
            <span className="text-sm">Back</span>
          </Link>
          <div className="flex items-center gap-3">
            <div className="w-12 h-12 bg-gradient-to-br from-[#003366] to-[#0055A4] rounded-xl flex items-center justify-center">
              <Brain className="w-6 h-6 text-white" />
            </div>
            <div>
              <h1 className="text-3xl font-bold">Placement Probability</h1>
              <p className="text-sm text-muted-foreground">Get your AI-powered placement prediction</p>
            </div>
          </div>
        </div>
      </div>

      {/* Main Content */}
      <div className="max-w-4xl mx-auto px-6 py-8">
        {/* Progress Steps */}
        <div className="mb-8">
          <div className="flex items-center justify-between mb-4">
            <span className="text-sm font-medium text-muted-foreground">
              Step {step + 1} of {steps.length}
            </span>
            <div className="w-64 h-2 bg-muted rounded-full overflow-hidden">
              <div 
                className="h-full bg-gradient-to-r from-[#003366] to-[#0055A4] transition-all duration-300"
                style={{ width: `${((step + 1) / steps.length) * 100}%` }}
              />
            </div>
          </div>
          <div>
            <h2 className="text-2xl font-bold">{steps[step]?.title}</h2>
            <p className="text-sm text-muted-foreground mt-1">{steps[step]?.subtitle}</p>
          </div>
        </div>

        {/* Content Area */}
        <motion.div
          key={step}
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          exit={{ opacity: 0, y: -20 }}
          transition={{ duration: 0.3 }}
        >
          <Card className="p-8">
            {step === 0 && (
              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium mb-2">Student ID</label>
                  <Input
                    type="number"
                    placeholder="Enter your student ID (e.g., 200001)"
                    value={studentId}
                    onChange={(e) => setStudentId(e.target.value)}
                    className="h-12"
                  />
                </div>
              </div>
            )}

            {step === 1 && (
              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium mb-2">LeetCode Username (Optional)</label>
                  <div className="flex gap-2">
                    <Input
                      placeholder="Enter your LeetCode username"
                      value={leetcodeUsername}
                      onChange={(e) => setLeetcodeUsername(e.target.value)}
                      className="h-12"
                    />
                    <Button 
                      onClick={fetchLeetcodeScore}
                      disabled={fetchingLeetcode}
                      className="bg-[#003366] hover:bg-[#003366]/90"
                    >
                      {fetchingLeetcode ? <Loader2 className="w-4 h-4 animate-spin" /> : "Fetch"}
                    </Button>
                  </div>
                </div>
                <div>
                  <label className="block text-sm font-medium mb-2">DSA Score (0-100)</label>
                  <Input
                    type="number"
                    min="0"
                    max="100"
                    placeholder="Enter your DSA score"
                    value={formData.dsa_score || ""}
                    onChange={(e) => setFormData(prev => ({ ...prev, dsa_score: e.target.value ? parseInt(e.target.value) : null }))}
                    className="h-12"
                  />
                </div>
              </div>
            )}

            {step === 2 && (
              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium mb-3">GitHub Repository Links</label>
                  
                  <div className="space-y-3 mb-4">
                    <div className="flex gap-2">
                      <Input
                        placeholder="Enter GitHub repository URL (e.g., https://github.com/username/repo)"
                        value={currentRepoInput}
                        onChange={(e) => setCurrentRepoInput(e.target.value)}
                        className="h-12"
                      />
                      <Button 
                        onClick={addGithubRepo}
                        className="bg-[#003366] hover:bg-[#003366]/90"
                      >
                        Add Repo
                      </Button>
                    </div>
                    
                    {githubRepoLinks.length > 0 && (
                      <div className="space-y-2">
                        <p className="text-sm font-medium text-muted-foreground">Added Repositories ({githubRepoLinks.length}):</p>
                        {githubRepoLinks.map((link, idx) => (
                          <div key={idx} className="flex items-center justify-between p-3 bg-muted rounded-lg">
                            <span className="text-sm truncate flex-1">{link}</span>
                            <Button
                              variant="ghost"
                              size="sm"
                              onClick={() => removeGithubRepo(idx)}
                              className="text-destructive hover:text-destructive"
                            >
                              ✕
                            </Button>
                          </div>
                        ))}
                      </div>
                    )}
                  </div>

                  <Button
                    onClick={analyzeGithubProjects}
                    disabled={githubRepoLinks.length === 0 || analyzingGithub}
                    className="w-full bg-green-600 hover:bg-green-600/90"
                  >
                    {analyzingGithub ? (
                      <><Loader2 className="w-4 h-4 animate-spin mr-2" /> Analyzing...</>
                    ) : (
                      `Analyze Projects (${githubRepoLinks.length} repos)`
                    )}
                  </Button>
                </div>

                {githubReport && (
                  <Card className="p-4 bg-green-50 border-green-200">
                    <p className="text-sm text-green-700">
                      ✓ Project Score: <span className="font-bold">{formData.project_score}/100</span>
                    </p>
                    <p className="text-xs text-green-600 mt-2">
                      {githubReport.total_projects} project(s) analyzed
                    </p>
                  </Card>
                )}

                {!formData.project_score && (
                  <div>
                    <label className="block text-sm font-medium mb-2">Or Enter Manually (0-100)</label>
                    <Input
                      type="number"
                      min="0"
                      max="100"
                      placeholder="Enter your project score manually"
                      value={formData.project_score || ""}
                      onChange={(e) => setFormData(prev => ({ ...prev, project_score: e.target.value ? parseInt(e.target.value) : null }))}
                      className="h-12"
                    />
                  </div>
                )}
              </div>
            )}

            {step === 3 && (
              <div className="space-y-4">
                <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
                  <p className="text-sm text-blue-700 mb-3 font-medium">📋 Aptitude Test</p>
                  <p className="text-sm text-blue-600 mb-4">
                    Visit the website to take the aptitude test and note your score.
                  </p>
                  <Button 
                    onClick={() => aptitudeAtsInfo && openLink(aptitudeAtsInfo.aptitude.link)}
                    className="w-full gap-2 bg-blue-600 hover:bg-blue-700"
                  >
                    <ExternalLink className="w-4 h-4" />
                    Take Aptitude Test
                  </Button>
                </div>

                <div>
                  <label className="block text-sm font-medium mb-2">Aptitude Score (0-100)</label>
                  <Input
                    type="number"
                    min="0"
                    max="100"
                    placeholder="Enter your aptitude score"
                    value={formData.aptitude_score || ""}
                    onChange={(e) => setFormData(prev => ({ ...prev, aptitude_score: e.target.value ? parseInt(e.target.value) : null }))}
                    className="h-12"
                  />
                </div>
              </div>
            )}

            {step === 4 && (
              <div className="space-y-4">
                <div className="bg-purple-50 border border-purple-200 rounded-lg p-4">
                  <p className="text-sm text-purple-700 mb-3 font-medium">📄 Resume ATS Checker</p>
                  <p className="text-sm text-purple-600 mb-4">
                    Upload your resume to get your ATS compatibility score.
                  </p>
                  <Button 
                    onClick={() => aptitudeAtsInfo && openLink(aptitudeAtsInfo.ats.link)}
                    className="w-full gap-2 bg-purple-600 hover:bg-purple-700"
                  >
                    <ExternalLink className="w-4 h-4" />
                    Check Resume ATS
                  </Button>
                </div>

                <div>
                  <label className="block text-sm font-medium mb-2">Resume ATS Score (0-100)</label>
                  <Input
                    type="number"
                    min="0"
                    max="100"
                    placeholder="Enter your resume ATS score"
                    value={formData.resume_ats_score || ""}
                    onChange={(e) => setFormData(prev => ({ ...prev, resume_ats_score: e.target.value ? parseInt(e.target.value) : null }))}
                    className="h-12"
                  />
                </div>
              </div>
            )}

            {step === 5 && (
              <div className="space-y-6">
                <div className="bg-orange-50 border border-orange-200 rounded-lg p-3">
                  <p className="text-sm text-orange-700">
                    🎤 Please answer the following questions honestly in 5-8 sentences each.
                  </p>
                </div>

                {hrQuestions.map((q, idx) => (
                  <div key={q.id} className="space-y-2">
                    <label className="block text-sm font-medium">
                      Q{idx + 1}. {q.text}
                    </label>
                    <Textarea
                      placeholder="Your answer..."
                      value={q.answer}
                      onChange={(e) => updateHRAnswer(q.id, e.target.value)}
                      className="min-h-24"
                    />
                  </div>
                ))}

                <Button
                  onClick={evaluateHRRound}
                  disabled={evaluatingHR}
                  className="w-full bg-orange-600 hover:bg-orange-700"
                >
                  {evaluatingHR ? (
                    <><Loader2 className="w-4 h-4 animate-spin mr-2" /> Evaluating...</>
                  ) : (
                    "Evaluate HR Responses"
                  )}
                </Button>

                {formData.hr_score && (
                  <Card className="p-4 bg-green-50 border-green-200">
                    <p className="text-sm text-green-700">
                      ✓ HR Score: <span className="font-bold">{formData.hr_score}/100</span>
                    </p>
                  </Card>
                )}
              </div>
            )}

            {step === 6 && (
              <div className="flex flex-col items-center justify-center py-12">
                <div className="animate-spin mb-4">
                  <div className="w-16 h-16 border-4 border-[#003366]/20 border-t-[#003366] rounded-full"></div>
                </div>
                <p className="text-lg font-medium text-center">Analyzing your profile with AI...</p>
                <p className="text-sm text-muted-foreground mt-2">This may take a few moments</p>
              </div>
            )}

            {step === 7 && predictions && (
              <div className="space-y-6">
                <div className="flex items-center gap-3 text-green-600 mb-6">
                  <CheckCircle2 className="w-6 h-6" />
                  <span className="font-medium">Predictions Generated Successfully!</span>
                </div>
                
                <div className="grid grid-cols-2 gap-4">
                  <Card className="bg-gradient-to-br from-[#003366]/10 to-[#0055A4]/10 p-4">
                    <p className="text-sm text-muted-foreground">Placement Probability</p>
                    <p className="text-3xl font-bold text-[#003366]">{predictions.overall_placement_probability}%</p>
                  </Card>
                  
                  <Card className="bg-gradient-to-br from-[#10B981]/10 to-[#059669]/10 p-4">
                    <p className="text-sm text-muted-foreground">Predicted Salary</p>
                    <p className="text-3xl font-bold text-[#10B981]">₹{predictions.predicted_salary_lpa} LPA</p>
                  </Card>
                </div>

                <Card className="p-4 bg-gradient-to-br from-[#FFC107]/10 to-[#F59E0B]/10">
                  <p className="text-sm text-muted-foreground mb-2">Predicted Job Role</p>
                  <p className="text-xl font-bold text-[#FFC107]">{predictions.predicted_job_role}</p>
                </Card>

                <Card className="p-4">
                  <p className="text-sm text-muted-foreground mb-3">Top Recommended Companies</p>
                  <div className="flex flex-wrap gap-2">
                    {predictions.recommended_companies?.map((company: string) => (
                      <span key={company} className="px-3 py-1 bg-[#003366]/10 text-[#003366] rounded-full text-sm font-medium">
                        {company}
                      </span>
                    ))}
                  </div>
                </Card>

                <Link to="/predictions">
                  <Button className="w-full h-12 bg-gradient-to-r from-[#003366] to-[#0055A4] hover:opacity-90">
                    View Full Results
                  </Button>
                </Link>
              </div>
            )}

            {/* Error Display */}
            {error && (
              <div className="flex items-center gap-2 p-4 bg-destructive/10 text-destructive rounded-lg">
                <AlertCircle className="w-5 h-5 shrink-0" />
                <span className="text-sm">{error}</span>
              </div>
            )}
          </Card>
        </motion.div>

        {/* Action Buttons */}
        {step < 7 && (
          <div className="flex gap-4 mt-8">
            <Button 
              variant="outline"
              onClick={goBack}
              className="flex-1 h-12"
            >
              Back
            </Button>
            <Button 
              onClick={goNext}
              disabled={loading || analyzingGithub || evaluatingHR || fetchingLeetcode}
              className="flex-1 h-12 bg-gradient-to-r from-[#003366] to-[#0055A4] hover:opacity-90"
            >
              {loading ? <Loader2 className="w-4 h-4 animate-spin mr-2" /> : null}
              {step === 5 ? "Generate Predictions" : "Next"}
            </Button>
          </div>
        )}
      </div>
    </div>
  );
}
