import type { Metadata } from 'next'
import { Inter } from 'next/font/google'
import './globals.css'
import HeaderNav from "../components/HeaderNav";

const inter = Inter({ 
  subsets: ['latin'],
  display: 'swap',
  preload: true,
  fallback: ['system-ui', 'arial'],
})

export const metadata: Metadata = {
  title: 'Lave-linge Durables | Solutions pour Investisseurs Immobiliers',
  description: 'Découvrez les meilleurs lave-linge durables et réparables pour investisseurs immobiliers. Maximisez la valeur de votre propriété.',
  keywords: 'lave-linge, durabilité, réparabilité, investissement immobilier, électroménager',
  title: 'Lave-linge Durables | Solutions pour Investisseurs Immobiliers',
  description: 'Découvrez les meilleurs lave-linge durables et réparables pour investisseurs immobiliers. Maximisez la valeur de votre propriété.',
  keywords: 'lave-linge, durabilité, réparabilité, investissement immobilier, électroménager',
  metadataBase: new URL(process.env.NEXT_PUBLIC_SITE_URL || 'http://localhost:3000'),
  openGraph: {
    title: 'Lave-linge Durables | Solutions pour Investisseurs Immobiliers',
    description: 'Maximisez la valeur de votre propriété avec nos lave-linge durables',
    title: 'Lave-linge Durables | Solutions pour Investisseurs Immobiliers',
    description: 'Maximisez la valeur de votre propriété avec nos lave-linge durables',
    type: 'website',
  },
  twitter: {
    card: 'summary_large_image',
    title: 'Lave-linge Durables | Solutions pour Investisseurs Immobiliers',
    description: 'Maximisez la valeur de votre propriété avec nos lave-linge durables',
    title: 'Lave-linge Durables | Solutions pour Investisseurs Immobiliers',
    description: 'Maximisez la valeur de votre propriété avec nos lave-linge durables',
  },
  robots: {
    index: true,
    follow: true,
    googleBot: {
      index: true,
      follow: true,
      'max-video-preview': -1,
      'max-image-preview': 'large',
      'max-snippet': -1,
    },
  },
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="fr">
      <head>
        <link rel="preconnect" href="https://fonts.gstatic.com/" crossOrigin="" />
        <link
          rel="stylesheet"
          href="https://fonts.googleapis.com/css2?display=swap&family=Noto+Sans%3Awght%40400%3B500%3B700%3B900&family=Public+Sans%3Awght%40400%3B500%3B700%3B900"
        />
      </head>
      <body className={inter.className} style={{fontFamily: '"Public Sans", "Noto Sans", sans-serif'}}>
        <div className="relative flex size-full min-h-screen flex-col bg-white group/design-root overflow-x-hidden">
          <div className="layout-container flex h-full grow flex-col">
            <HeaderNav />
            <main>{children}</main>
            <footer className="flex justify-center">
              <div className="flex max-w-[960px] flex-1 flex-col">
                <footer className="flex flex-col gap-6 px-5 py-10 text-center @container">
                  <div className="flex flex-wrap items-center justify-center gap-6 @[480px]:flex-row @[480px]:justify-around">
                    <a className="text-[#637588] text-base font-normal leading-normal min-w-40" href="#">Politique de Confidentialité</a>
                    <a className="text-[#637588] text-base font-normal leading-normal min-w-40" href="#">Conditions d'Utilisation</a>
                    <a className="text-[#637588] text-base font-normal leading-normal min-w-40" href="#">Nous Contacter</a>
                  </div>
                  <p className="text-[#637588] text-base font-normal leading-normal">© 2025 Laundry Solutions. Tous droits réservés.</p>
                </footer>
              </div>
            </footer>
          </div>
        </div>
      </body>
    </html>
  )
}
