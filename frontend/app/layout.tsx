import type { Metadata } from 'next'
import { Inter } from 'next/font/google'
import './globals.css'

const inter = Inter({ subsets: ['latin'] })

export const metadata: Metadata = {
  title: 'Meilleurs Lave-linge Durables 2025 | Comparatif et Avis',
  description: 'Découvrez les meilleurs lave-linge durables et réparables en 2025. Comparatif complet avec notes de réparabilité et fiabilité. Achetez en toute confiance.',
  keywords: 'lave-linge, durabilité, réparabilité, comparatif, 2025, électroménager',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="fr">
      <body className={inter.className}>
        <div className="min-h-screen bg-gray-50">
          {/* Colorful Header */}
          <header className="bg-gradient-to-r from-blue-600 to-blue-700 shadow-lg">
            <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
              <div className="flex justify-between items-center py-4">
                <div className="flex items-center">
                  <div className="flex items-center space-x-2">
                    <div className="w-8 h-8 bg-white rounded-full flex items-center justify-center">
                      <span className="text-blue-600 font-bold text-lg">⚡</span>
                    </div>
                    <h1 className="text-2xl font-bold text-white">
                      Lave-linge Durables
                    </h1>
                  </div>
                </div>
                <nav className="hidden md:flex space-x-8">
                  <a href="#" className="text-blue-100 hover:text-white transition-colors">Comparatif</a>
                  <a href="#" className="text-blue-100 hover:text-white transition-colors">Guides</a>
                  <a href="#" className="text-blue-100 hover:text-white transition-colors">Avis</a>
                  <a href="#" className="text-blue-100 hover:text-white transition-colors">Contact</a>
                </nav>
                <div className="flex items-center space-x-4">
                  <div className="relative">
                    <input
                      type="text"
                      placeholder="Rechercher..."
                      className="w-48 px-4 py-2 rounded-lg bg-blue-500 text-white placeholder-blue-200 border border-blue-400 focus:outline-none focus:ring-2 focus:ring-white"
                    />
                    <span className="absolute right-3 top-2.5 text-blue-200">🔍</span>
                  </div>
                </div>
              </div>
            </div>
          </header>
          <main>{children}</main>
          <footer className="bg-white border-t mt-16">
            <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
              <div className="text-center text-gray-600">
                <p>&copy; 2025 Lave-linge Durables. Comparatif indépendant et gratuit.</p>
              </div>
            </div>
          </footer>
        </div>
      </body>
    </html>
  )
}
