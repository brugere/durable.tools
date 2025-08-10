import type { Metadata } from 'next'
import { Inter } from 'next/font/google'
import './globals.css'

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
  metadataBase: new URL(process.env.NEXT_PUBLIC_SITE_URL || 'http://localhost:3000'),
  openGraph: {
    title: 'Lave-linge Durables | Solutions pour Investisseurs Immobiliers',
    description: 'Maximisez la valeur de votre propriété avec nos lave-linge durables',
    type: 'website',
  },
  twitter: {
    card: 'summary_large_image',
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
            <header className="flex items-center justify-between whitespace-nowrap border-b border-solid border-b-[#f0f2f4] px-10 py-3">
              <div className="flex items-center gap-8">
                <div className="flex items-center gap-4 text-[#111418]">
                  <div className="size-4">
                    <svg viewBox="0 0 48 48" fill="none" xmlns="http://www.w3.org/2000/svg">
                      <path
                        d="M42.4379 44C42.4379 44 36.0744 33.9038 41.1692 24C46.8624 12.9336 42.2078 4 42.2078 4L7.01134 4C7.01134 4 11.6577 12.932 5.96912 23.9969C0.876273 33.9029 7.27094 44 7.27094 44L42.4379 44Z"
                        fill="currentColor"
                      ></path>
                    </svg>
                  </div>
                  <h2 className="text-[#111418] text-lg font-bold leading-tight tracking-[-0.015em]">Laundry Solutions</h2>
                </div>
                <div className="flex items-center gap-9">
                  <a className="text-[#111418] text-sm font-medium leading-normal" href="#">Produits</a>
                  <a className="text-[#111418] text-sm font-medium leading-normal" href="#">Services</a>
                  <a className="text-[#111418] text-sm font-medium leading-normal" href="#">Support</a>
                  <a className="text-[#111418] text-sm font-medium leading-normal" href="#">À Propos</a>
                </div>
              </div>
              <div className="flex flex-1 justify-end gap-8">
                <label className="flex flex-col min-w-40 !h-10 max-w-64">
                  <div className="flex w-full flex-1 items-stretch rounded-lg h-full">
                    <div
                      className="text-[#637588] flex border-none bg-[#f0f2f4] items-center justify-center pl-4 rounded-l-lg border-r-0"
                      data-icon="MagnifyingGlass"
                      data-size="24px"
                      data-weight="regular"
                    >
                      <svg xmlns="http://www.w3.org/2000/svg" width="24px" height="24px" fill="currentColor" viewBox="0 0 256 256">
                        <path
                          d="M229.66,218.34l-50.07-50.06a88.11,88.11,0,1,0-11.31,11.31l50.06,50.07a8,8,0,0,0,11.32-11.32ZM40,112a72,72,0,1,1,72,72A72.08,72.08,0,0,1,40,112Z"
                        ></path>
                      </svg>
                    </div>
                    <input
                      placeholder="Rechercher"
                      className="form-input flex w-full min-w-0 flex-1 resize-none overflow-hidden rounded-lg text-[#111418] focus:outline-0 focus:ring-0 border-none bg-[#f0f2f4] focus:border-none h-full placeholder:text-[#637588] px-4 rounded-l-none border-l-0 pl-2 text-base font-normal leading-normal"
                      defaultValue=""
                    />
                  </div>
                </label>
                <button
                  className="flex min-w-[84px] max-w-[480px] cursor-pointer items-center justify-center overflow-hidden rounded-lg h-10 px-4 bg-[#1773cf] text-white text-sm font-bold leading-normal tracking-[0.015em]"
                >
                  <span className="truncate">Contacter les Ventes</span>
                </button>
              </div>
            </header>
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
