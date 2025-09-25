import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Rocket, Bot, DollarSign, Users, Zap, Code } from "lucide-react"

export default function Home() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100">
      {/* Header */}
      <header className="container mx-auto px-4 py-6">
        <nav className="flex items-center justify-between">
          <div className="flex items-center space-x-2">
            <Rocket className="h-8 w-8 text-blue-600" />
            <span className="text-2xl font-bold text-gray-900">my-yc</span>
          </div>
          <div className="flex items-center space-x-4">
            <Button variant="ghost">Login</Button>
            <Button>Get Started</Button>
          </div>
        </nav>
      </header>

      <div className="container mx-auto px-4 py-16">
        {/* Hero Section */}
        <div className="text-center mb-16">
          <h1 className="text-5xl font-bold mb-6 bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">
            Your Personal Y Combinator
          </h1>
          <p className="text-xl text-gray-600 mb-8 max-w-2xl mx-auto">
            Transform ideas into reality with autonomous AI agents. Launch multiple startups
            like a seasoned investor, with zero operational overhead.
          </p>
          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <Button size="lg" className="text-lg px-8 py-3">
              <Rocket className="mr-2 h-5 w-5" />
              Launch Your First Startup
            </Button>
            <Button variant="outline" size="lg" className="text-lg px-8 py-3">
              View Demo Projects
            </Button>
          </div>
        </div>

        {/* Features Grid */}
        <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-8 mb-16">
          <Card className="transition-transform hover:scale-105">
            <CardHeader>
              <Bot className="h-12 w-12 text-blue-600 mb-2" />
              <CardTitle>Autonomous Execution</CardTitle>
              <CardDescription>
                AI agents handle everything from coding to deployment
              </CardDescription>
            </CardHeader>
            <CardContent>
              <p className="text-gray-600">
                Your agents autonomously create GitHub repos, build applications,
                set up databases, and deploy to production.
              </p>
            </CardContent>
          </Card>

          <Card className="transition-transform hover:scale-105">
            <CardHeader>
              <Zap className="h-12 w-12 text-yellow-600 mb-2" />
              <CardTitle>Zero Idle Costs</CardTitle>
              <CardDescription>
                Serverless architecture scales to zero
              </CardDescription>
            </CardHeader>
            <CardContent>
              <p className="text-gray-600">
                Each startup runs independently and costs nothing when idle.
                Scale infinitely without infrastructure overhead.
              </p>
            </CardContent>
          </Card>

          <Card className="transition-transform hover:scale-105">
            <CardHeader>
              <Users className="h-12 w-12 text-green-600 mb-2" />
              <CardTitle>Portfolio Management</CardTitle>
              <CardDescription>
                Manage multiple startups like a VC fund
              </CardDescription>
            </CardHeader>
            <CardContent>
              <p className="text-gray-600">
                Track progress, monitor metrics, and make strategic decisions
                across your entire startup portfolio.
              </p>
            </CardContent>
          </Card>

          <Card className="transition-transform hover:scale-105">
            <CardHeader>
              <Code className="h-12 w-12 text-purple-600 mb-2" />
              <CardTitle>Full-Stack Creation</CardTitle>
              <CardDescription>
                Complete applications, not just prototypes
              </CardDescription>
            </CardHeader>
            <CardContent>
              <p className="text-gray-600">
                Agents create production-ready apps with databases,
                authentication, payments, and custom domains.
              </p>
            </CardContent>
          </Card>

          <Card className="transition-transform hover:scale-105">
            <CardHeader>
              <DollarSign className="h-12 w-12 text-red-600 mb-2" />
              <CardTitle>Revenue Generation</CardTitle>
              <CardDescription>
                Built-in monetization and analytics
              </CardDescription>
            </CardHeader>
            <CardContent>
              <p className="text-gray-600">
                Automatic Stripe setup, email marketing, and analytics
                integration to start generating revenue immediately.
              </p>
            </CardContent>
          </Card>

          <Card className="transition-transform hover:scale-105">
            <CardHeader>
              <Rocket className="h-12 w-12 text-indigo-600 mb-2" />
              <CardTitle>Rapid Deployment</CardTitle>
              <CardDescription>
                From idea to live startup in minutes
              </CardDescription>
            </CardHeader>
            <CardContent>
              <p className="text-gray-600">
                Submit an idea and watch agents create a fully functional
                startup complete with landing page, app, and infrastructure.
              </p>
            </CardContent>
          </Card>
        </div>

        {/* CTA Section */}
        <div className="text-center bg-white rounded-2xl p-12 shadow-lg">
          <h2 className="text-3xl font-bold mb-4 text-gray-900">Ready to become your own Y Combinator?</h2>
          <p className="text-gray-600 mb-8 text-lg max-w-2xl mx-auto">
            Join the future of entrepreneurship. Launch your first autonomous startup
            and begin building your portfolio today.
          </p>
          <Button size="lg" className="text-lg px-8 py-3">
            <Rocket className="mr-2 h-5 w-5" />
            Start Building - Free
          </Button>
          <p className="text-sm text-gray-500 mt-4">No credit card required • First startup free</p>
        </div>
      </div>

      {/* Footer */}
      <footer className="bg-gray-900 text-gray-300 py-12">
        <div className="container mx-auto px-4">
          <div className="text-center">
            <div className="flex items-center justify-center space-x-2 mb-4">
              <Rocket className="h-6 w-6 text-blue-400" />
              <span className="text-xl font-bold text-white">my-yc</span>
            </div>
            <p className="text-gray-400">
              Democratizing entrepreneurship through autonomous AI agents
            </p>
            <div className="mt-6 text-sm text-gray-500">
              © 2024 my-yc. All rights reserved.
            </div>
          </div>
        </div>
      </footer>
    </div>
  )
}