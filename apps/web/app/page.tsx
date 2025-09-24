import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"

export default function Home() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100">
      <div className="container mx-auto px-4 py-16">
        <div className="text-center mb-16">
          <h1 className="text-5xl font-bold mb-6 bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">
            my-yc
          </h1>
          <p className="text-xl text-gray-600 mb-8 max-w-2xl mx-auto">
            Transform ideas into reality with autonomous AI agents. Be the YC of your own startup portfolio.
          </p>
          <Button size="lg" className="mr-4">
            Launch Your First Startup
          </Button>
          <Button variant="outline" size="lg">
            View Portfolio
          </Button>
        </div>

        <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-8 mb-16">
          <Card>
            <CardHeader>
              <CardTitle>🚀 Full-Stack Execution</CardTitle>
              <CardDescription>
                Beyond brainstorming - agents build real products
              </CardDescription>
            </CardHeader>
            <CardContent>
              <p className="text-gray-600">
                Your AI agents handle everything from market research to deployment,
                creating complete startups with minimal human intervention.
              </p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>🤖 Autonomous Operation</CardTitle>
              <CardDescription>
                Projects run independently after launch
              </CardDescription>
            </CardHeader>
            <CardContent>
              <p className="text-gray-600">
                Each startup becomes a self-contained entity that provisions
                its own infrastructure and manages its own services.
              </p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>💰 Zero Idle Costs</CardTitle>
              <CardDescription>
                Serverless architecture scales to zero
              </CardDescription>
            </CardHeader>
            <CardContent>
              <p className="text-gray-600">
                Pay only when your startups are actively working.
                Idle projects cost you nothing.
              </p>
            </CardContent>
          </Card>
        </div>

        <div className="text-center">
          <h2 className="text-3xl font-bold mb-4">Ready to become your own Y Combinator?</h2>
          <p className="text-gray-600 mb-8">
            Start your first autonomous startup today and manage multiple AI-powered ventures
            like a seasoned investor.
          </p>
          <Button size="lg">Get Started - Free</Button>
        </div>
      </div>
    </div>
  )
}