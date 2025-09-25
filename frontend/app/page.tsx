import { Button } from "@/components/ui/button"
import { Textarea } from "@/components/ui/textarea"
import { Sparkles, Send } from "lucide-react"

export default function Home() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-purple-50 via-white to-blue-50">
      {/* Header */}
      <header className="border-b border-gray-100 bg-white/80 backdrop-blur-sm">
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
                Examples
              </Button>
              <Button variant="ghost" className="text-gray-600 hover:text-gray-900">
                Docs
              </Button>
              <Button className="bg-purple-600 hover:bg-purple-700">
                Sign In
              </Button>
            </div>
          </nav>
        </div>
      </header>

      {/* Main Content */}
      <main className="container mx-auto px-4 py-16">
        <div className="max-w-4xl mx-auto">
          {/* Hero */}
          <div className="text-center mb-16">
            <h1 className="text-5xl md:text-6xl font-bold tracking-tight mb-6">
              <span className="bg-gradient-to-r from-gray-900 via-purple-800 to-purple-600 bg-clip-text text-transparent">
                Launch startups
              </span>
              <br />
              <span className="text-gray-900">with AI agents</span>
            </h1>

            <p className="text-xl text-gray-600 mb-12 max-w-2xl mx-auto leading-relaxed">
              Describe your startup idea and watch AI agents autonomously create
              repositories, build applications, and deploy to production.
            </p>
          </div>

          {/* Chat Interface */}
          <div className="bg-white rounded-2xl shadow-2xl border border-gray-200 max-w-3xl mx-auto">
            {/* Chat Header */}
            <div className="border-b border-gray-100 px-6 py-4">
              <div className="flex items-center space-x-3">
                <div className="w-3 h-3 bg-green-500 rounded-full animate-pulse"></div>
                <span className="font-medium text-gray-900">AI Agent Team</span>
                <span className="text-sm text-gray-500">Ready to build your startup</span>
              </div>
            </div>

            {/* Chat Messages */}
            <div className="h-96 overflow-y-auto p-6 space-y-4">
              {/* Agent Message */}
              <div className="flex items-start space-x-3">
                <div className="w-8 h-8 bg-gradient-to-r from-purple-500 to-purple-600 rounded-full flex items-center justify-center flex-shrink-0">
                  <Sparkles className="w-4 h-4 text-white" />
                </div>
                <div className="bg-gray-50 rounded-2xl px-4 py-3 max-w-md">
                  <p className="text-gray-800">
                    👋 Hi! I&apos;m your AI agent team. Describe your startup idea and I&apos;ll
                    create a complete application with:
                  </p>
                  <ul className="mt-2 text-sm text-gray-600 space-y-1">
                    <li>• GitHub repository</li>
                    <li>• Next.js application</li>
                    <li>• Database setup</li>
                    <li>• Vercel deployment</li>
                  </ul>
                </div>
              </div>

              {/* Example User Message */}
              <div className="flex items-start space-x-3 justify-end">
                <div className="bg-purple-600 rounded-2xl px-4 py-3 max-w-md">
                  <p className="text-white">
                    Create an AI recipe app for health-conscious users
                  </p>
                </div>
                <div className="w-8 h-8 bg-gray-200 rounded-full flex items-center justify-center flex-shrink-0">
                  <span className="text-sm font-medium text-gray-600">You</span>
                </div>
              </div>

              {/* Agent Working Message */}
              <div className="flex items-start space-x-3">
                <div className="w-8 h-8 bg-gradient-to-r from-purple-500 to-purple-600 rounded-full flex items-center justify-center flex-shrink-0">
                  <Sparkles className="w-4 h-4 text-white" />
                </div>
                <div className="bg-gray-50 rounded-2xl px-4 py-3 max-w-md">
                  <div className="space-y-2">
                    <p className="text-gray-800 font-medium">🚀 Creating your startup...</p>
                    <div className="text-sm font-mono space-y-1 text-gray-600">
                      <div className="text-green-600">✅ Created GitHub repo: ai-recipe-app</div>
                      <div className="text-blue-600">⚡ Setting up Next.js structure</div>
                      <div className="text-purple-600">🔧 Generating components</div>
                      <div className="text-orange-600 flex items-center">
                        <div className="w-2 h-2 bg-orange-500 rounded-full animate-pulse mr-2"></div>
                        Deploying to Vercel...
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>

            {/* Chat Input */}
            <div className="border-t border-gray-100 p-6">
              <div className="flex space-x-3">
                <Textarea
                  placeholder="Describe your startup idea (e.g., 'AI-powered recipe app for healthy eating')"
                  className="flex-1 resize-none min-h-[60px] border-gray-200 focus:border-purple-500 focus:ring-purple-500"
                />
                <Button size="lg" className="bg-purple-600 hover:bg-purple-700 px-6">
                  <Send className="w-4 h-4" />
                </Button>
              </div>
              <p className="text-xs text-gray-500 mt-2 text-center">
                Press Enter to send • Your startup will be ready in ~3 minutes
              </p>
            </div>
          </div>

          {/* Simple Footer */}
          <div className="text-center mt-16 text-gray-500 text-sm">
            <p>Built with ❤️ by autonomous AI agents</p>
          </div>
        </div>
      </main>
    </div>
  )
}