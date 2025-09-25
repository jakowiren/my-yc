import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import {
  Sparkles,
  Bot,
  Zap,
  Target,
  Code,
  Database,
  Globe,
  ArrowRight,
  CheckCircle,
  PlayCircle,
  Github,
  Rocket,
  TrendingUp,
  Users
} from "lucide-react"

export default function Home() {
  return (
    <div className="min-h-screen bg-white">
      {/* Header */}
      <header className="border-b border-gray-100 bg-white/80 backdrop-blur-sm sticky top-0 z-50">
        <div className="container mx-auto px-4 py-4">
          <nav className="flex items-center justify-between">
            <div className="flex items-center space-x-2">
              <div className="flex items-center justify-center w-8 h-8 bg-gradient-to-r from-purple-600 to-purple-700 rounded-lg">
                <Sparkles className="h-5 w-5 text-white" />
              </div>
              <span className="text-2xl font-bold bg-gradient-to-r from-purple-600 to-purple-700 bg-clip-text text-transparent">
                my-yc
              </span>
            </div>
            <div className="flex items-center space-x-4">
              <Button variant="ghost" className="text-gray-600 hover:text-gray-900">
                Documentation
              </Button>
              <Button variant="ghost" className="text-gray-600 hover:text-gray-900">
                Examples
              </Button>
              <Button className="bg-purple-600 hover:bg-purple-700">
                Get Started
              </Button>
            </div>
          </nav>
        </div>
      </header>

      {/* Hero Section */}
      <section className="py-20 md:py-32">
        <div className="container mx-auto px-4">
          <div className="max-w-4xl mx-auto text-center">
            <Badge variant="secondary" className="mb-6 bg-purple-50 text-purple-700 border-purple-200">
              <Sparkles className="w-3 h-3 mr-1" />
              Your Personal Y Combinator
            </Badge>

            <h1 className="text-5xl md:text-7xl font-bold tracking-tight mb-8">
              <span className="bg-gradient-to-r from-gray-900 via-purple-800 to-purple-600 bg-clip-text text-transparent">
                Launch startups
              </span>
              <br />
              <span className="text-gray-900">with AI agents</span>
            </h1>

            <p className="text-xl md:text-2xl text-gray-600 mb-10 max-w-3xl mx-auto leading-relaxed">
              Transform ideas into production-ready startups. Watch AI agents autonomously create
              repositories, build applications, and deploy to the cloud—all in real-time.
            </p>

            <div className="flex flex-col sm:flex-row gap-4 justify-center items-center mb-12">
              <Button size="lg" className="text-lg px-8 py-4 bg-purple-600 hover:bg-purple-700 h-14">
                <PlayCircle className="mr-2 h-5 w-5" />
                Watch Demo
              </Button>
              <Button variant="outline" size="lg" className="text-lg px-8 py-4 h-14 border-gray-300">
                View Portfolio
                <ArrowRight className="ml-2 h-4 w-4" />
              </Button>
            </div>

            {/* Live Demo Terminal Preview */}
            <div className="bg-gray-900 rounded-xl p-6 text-left max-w-2xl mx-auto shadow-2xl border">
              <div className="flex items-center mb-4">
                <div className="flex space-x-2">
                  <div className="w-3 h-3 bg-red-500 rounded-full"></div>
                  <div className="w-3 h-3 bg-yellow-500 rounded-full"></div>
                  <div className="w-3 h-3 bg-green-500 rounded-full"></div>
                </div>
                <span className="ml-4 text-gray-400 text-sm font-medium">AI Agent Terminal</span>
              </div>
              <div className="font-mono text-sm space-y-2">
                <div className="text-green-400">🤖 [github] Creating repository: ai-recipe-app-abc123</div>
                <div className="text-blue-400">🤖 [github] Setting up Next.js project structure</div>
                <div className="text-purple-400">🤖 [github] Generated 8 files (package.json, app/page.tsx...)</div>
                <div className="text-green-400">🤖 [github] ✅ Startup ready for deployment!</div>
                <div className="text-gray-500">🤖 [deploy] 🚀 Live at: https://ai-recipe-app.vercel.app</div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section className="py-20 bg-gray-50">
        <div className="container mx-auto px-4">
          <div className="text-center mb-16">
            <h2 className="text-4xl font-bold text-gray-900 mb-4">
              The complete startup accelerator
            </h2>
            <p className="text-xl text-gray-600 max-w-2xl mx-auto">
              From idea to IPO-ready. Our AI agents handle the entire startup lifecycle
              with the expertise of seasoned entrepreneurs.
            </p>
          </div>

          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-8">
            {/* Feature 1 */}
            <Card className="border-0 shadow-lg bg-white hover:shadow-xl transition-all duration-300 group">
              <CardHeader>
                <div className="w-12 h-12 bg-purple-100 rounded-lg flex items-center justify-center mb-4 group-hover:bg-purple-200 transition-colors">
                  <Bot className="h-6 w-6 text-purple-600" />
                </div>
                <CardTitle className="text-xl">Autonomous Development</CardTitle>
                <CardDescription className="text-gray-600">
                  AI agents write code, create databases, and deploy applications
                </CardDescription>
              </CardHeader>
              <CardContent>
                <ul className="space-y-3">
                  <li className="flex items-center text-sm text-gray-600">
                    <CheckCircle className="h-4 w-4 text-green-500 mr-2 flex-shrink-0" />
                    Full-stack Next.js applications
                  </li>
                  <li className="flex items-center text-sm text-gray-600">
                    <CheckCircle className="h-4 w-4 text-green-500 mr-2 flex-shrink-0" />
                    Database schema generation
                  </li>
                  <li className="flex items-center text-sm text-gray-600">
                    <CheckCircle className="h-4 w-4 text-green-500 mr-2 flex-shrink-0" />
                    Production-ready deployments
                  </li>
                </ul>
              </CardContent>
            </Card>

            {/* Feature 2 */}
            <Card className="border-0 shadow-lg bg-white hover:shadow-xl transition-all duration-300 group">
              <CardHeader>
                <div className="w-12 h-12 bg-blue-100 rounded-lg flex items-center justify-center mb-4 group-hover:bg-blue-200 transition-colors">
                  <Zap className="h-6 w-6 text-blue-600" />
                </div>
                <CardTitle className="text-xl">Real-Time Monitoring</CardTitle>
                <CardDescription className="text-gray-600">
                  Watch your startup come to life with live terminal output
                </CardDescription>
              </CardHeader>
              <CardContent>
                <ul className="space-y-3">
                  <li className="flex items-center text-sm text-gray-600">
                    <CheckCircle className="h-4 w-4 text-green-500 mr-2 flex-shrink-0" />
                    Live agent progress tracking
                  </li>
                  <li className="flex items-center text-sm text-gray-600">
                    <CheckCircle className="h-4 w-4 text-green-500 mr-2 flex-shrink-0" />
                    SSH-like terminal experience
                  </li>
                  <li className="flex items-center text-sm text-gray-600">
                    <CheckCircle className="h-4 w-4 text-green-500 mr-2 flex-shrink-0" />
                    WebSocket real-time updates
                  </li>
                </ul>
              </CardContent>
            </Card>

            {/* Feature 3 */}
            <Card className="border-0 shadow-lg bg-white hover:shadow-xl transition-all duration-300 group">
              <CardHeader>
                <div className="w-12 h-12 bg-green-100 rounded-lg flex items-center justify-center mb-4 group-hover:bg-green-200 transition-colors">
                  <Target className="h-6 w-6 text-green-600" />
                </div>
                <CardTitle className="text-xl">Portfolio Management</CardTitle>
                <CardDescription className="text-gray-600">
                  Manage multiple startups like a seasoned VC investor
                </CardDescription>
              </CardHeader>
              <CardContent>
                <ul className="space-y-3">
                  <li className="flex items-center text-sm text-gray-600">
                    <CheckCircle className="h-4 w-4 text-green-500 mr-2 flex-shrink-0" />
                    Multi-project dashboard
                  </li>
                  <li className="flex items-center text-sm text-gray-600">
                    <CheckCircle className="h-4 w-4 text-green-500 mr-2 flex-shrink-0" />
                    Performance analytics
                  </li>
                  <li className="flex items-center text-sm text-gray-600">
                    <CheckCircle className="h-4 w-4 text-green-500 mr-2 flex-shrink-0" />
                    Zero idle costs
                  </li>
                </ul>
              </CardContent>
            </Card>
          </div>
        </div>
      </section>

      {/* Tech Stack Section */}
      <section className="py-20">
        <div className="container mx-auto px-4">
          <div className="text-center mb-16">
            <h2 className="text-4xl font-bold text-gray-900 mb-4">
              Production-ready tech stack
            </h2>
            <p className="text-xl text-gray-600">
              Built on proven technologies that scale from zero to IPO
            </p>
          </div>

          <div className="grid md:grid-cols-3 gap-8 max-w-5xl mx-auto">
            <div className="text-center">
              <div className="w-16 h-16 bg-gradient-to-r from-purple-100 to-purple-200 rounded-2xl flex items-center justify-center mx-auto mb-6">
                <Globe className="h-8 w-8 text-purple-600" />
              </div>
              <h3 className="text-xl font-semibold mb-2">Frontend</h3>
              <p className="text-gray-600 mb-4">Next.js 14, React 18, Tailwind CSS</p>
              <Badge variant="secondary" className="bg-purple-50 text-purple-700">Deployed on Vercel</Badge>
            </div>

            <div className="text-center">
              <div className="w-16 h-16 bg-gradient-to-r from-blue-100 to-blue-200 rounded-2xl flex items-center justify-center mx-auto mb-6">
                <Database className="h-8 w-8 text-blue-600" />
              </div>
              <h3 className="text-xl font-semibold mb-2">Backend</h3>
              <p className="text-gray-600 mb-4">Supabase PostgreSQL, Edge Functions</p>
              <Badge variant="secondary" className="bg-blue-50 text-blue-700">Real-time WebSocket</Badge>
            </div>

            <div className="text-center">
              <div className="w-16 h-16 bg-gradient-to-r from-green-100 to-green-200 rounded-2xl flex items-center justify-center mx-auto mb-6">
                <Code className="h-8 w-8 text-green-600" />
              </div>
              <h3 className="text-xl font-semibold mb-2">AI Agents</h3>
              <p className="text-gray-600 mb-4">Modal containers, Python, MCP tools</p>
              <Badge variant="secondary" className="bg-green-50 text-green-700">Auto-scaling</Badge>
            </div>
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-20 bg-gradient-to-r from-purple-600 to-purple-700">
        <div className="container mx-auto px-4">
          <div className="max-w-4xl mx-auto text-center text-white">
            <h2 className="text-4xl md:text-5xl font-bold mb-6">
              Ready to become your own Y Combinator?
            </h2>
            <p className="text-xl text-purple-100 mb-8 max-w-2xl mx-auto">
              Join thousands of entrepreneurs building the future with autonomous AI agents.
              Launch your first startup in minutes, not months.
            </p>
            <div className="flex flex-col sm:flex-row gap-4 justify-center items-center">
              <Button size="lg" variant="secondary" className="text-lg px-8 py-4 bg-white text-purple-700 hover:bg-gray-100 h-14">
                <Rocket className="mr-2 h-5 w-5" />
                Start Building - Free
              </Button>
              <Button variant="outline" size="lg" className="text-lg px-8 py-4 h-14 border-white/30 text-white hover:bg-white/10">
                <Github className="mr-2 h-4 w-4" />
                View on GitHub
              </Button>
            </div>
            <p className="text-sm text-purple-200 mt-6">
              No credit card required • First startup free • Open source
            </p>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="bg-gray-900 text-gray-300 py-12">
        <div className="container mx-auto px-4">
          <div className="max-w-6xl mx-auto">
            <div className="grid md:grid-cols-4 gap-8 mb-8">
              <div>
                <div className="flex items-center space-x-2 mb-4">
                  <div className="flex items-center justify-center w-8 h-8 bg-gradient-to-r from-purple-600 to-purple-700 rounded-lg">
                    <Sparkles className="h-5 w-5 text-white" />
                  </div>
                  <span className="text-xl font-bold text-white">my-yc</span>
                </div>
                <p className="text-gray-400 text-sm">
                  Democratizing entrepreneurship through autonomous AI agents
                </p>
              </div>

              <div>
                <h4 className="font-semibold text-white mb-3">Product</h4>
                <ul className="space-y-2 text-sm text-gray-400">
                  <li><a href="#" className="hover:text-white transition-colors">Features</a></li>
                  <li><a href="#" className="hover:text-white transition-colors">Pricing</a></li>
                  <li><a href="#" className="hover:text-white transition-colors">Documentation</a></li>
                </ul>
              </div>

              <div>
                <h4 className="font-semibold text-white mb-3">Company</h4>
                <ul className="space-y-2 text-sm text-gray-400">
                  <li><a href="#" className="hover:text-white transition-colors">About</a></li>
                  <li><a href="#" className="hover:text-white transition-colors">Blog</a></li>
                  <li><a href="#" className="hover:text-white transition-colors">Careers</a></li>
                </ul>
              </div>

              <div>
                <h4 className="font-semibold text-white mb-3">Resources</h4>
                <ul className="space-y-2 text-sm text-gray-400">
                  <li><a href="#" className="hover:text-white transition-colors">GitHub</a></li>
                  <li><a href="#" className="hover:text-white transition-colors">Discord</a></li>
                  <li><a href="#" className="hover:text-white transition-colors">Support</a></li>
                </ul>
              </div>
            </div>

            <div className="border-t border-gray-800 pt-8 text-center">
              <p className="text-gray-500 text-sm">
                © 2024 my-yc. All rights reserved. Built with ❤️ by AI agents.
              </p>
            </div>
          </div>
        </div>
      </footer>
    </div>
  )
}