// frontend/app/page.tsx
export const dynamic = "force-dynamic";

import { Suspense } from "react";
import SearchBox from "@/components/SearchBox";
import MachineResults from "@/components/MachineResults";

export default function Home({
  searchParams,
}: {
  searchParams: { q?: string };
}) {
  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
      {/* Hero Section with Colorful Design */}
      <section className="py-12 md:py-16">
        <div className="text-center">
          <h1 className="text-4xl md:text-5xl font-bold text-gray-900 mb-6">
            Comparatif Des Meilleurs Lave-linge | 2025
          </h1>
          
          {/* Trust Box */}
          <div className="bg-gray-100 rounded-xl p-6 mb-8 max-w-4xl mx-auto">
            <div className="flex items-center justify-center space-x-4 mb-4">
              <div className="flex items-center space-x-2">
                <span className="text-yellow-500 text-2xl">⭐</span>
                <span className="text-blue-600 font-semibold">Pourquoi nous faire confiance ?</span>
              </div>
            </div>
            <p className="text-gray-700 text-lg leading-relaxed">
              Nous consacrons des centaines d'heures à tester les lave-linge et à fournir les informations 
              les plus précieuses à nos lecteurs. Apprenez-en plus sur nous et sur notre processus de test complet.
            </p>
            <div className="flex items-center justify-center space-x-6 mt-4 text-sm text-gray-600">
              <span>Dernière mise à jour le : 05.08.2025</span>
              <span className="flex items-center space-x-1">
                <span>👍</span>
                <span>J'ai trouvé cela utile: 42</span>
              </span>
            </div>
          </div>
          
          {/* Search Section */}
          <div className="max-w-2xl mx-auto">
            <SearchBox defaultValue={searchParams.q} />
          </div>
          
          {/* Quick Stats with Colors */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mt-12">
            <div className="text-center bg-white rounded-lg p-6 shadow-sm border border-gray-200">
              <div className="text-4xl font-bold text-blue-600 mb-2">150+</div>
              <div className="text-gray-600 font-medium">Modèles testés</div>
            </div>
            <div className="text-center bg-white rounded-lg p-6 shadow-sm border border-gray-200">
              <div className="text-4xl font-bold text-green-600 mb-2">4.8/5</div>
              <div className="text-gray-600 font-medium">Note moyenne</div>
            </div>
            <div className="text-center bg-white rounded-lg p-6 shadow-sm border border-gray-200">
              <div className="text-4xl font-bold text-purple-600 mb-2">100%</div>
              <div className="text-gray-600 font-medium">Indépendant</div>
            </div>
          </div>
        </div>
      </section>

      {/* Content Section with Two Columns */}
      <section className="mb-12">
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-12 items-start">
          {/* Left Column - Text Content */}
          <div className="space-y-6">
            <div>
              <h2 className="text-2xl font-bold text-gray-900 mb-4">
                Le lave-linge parfait existe-t-il ?
              </h2>
              <p className="text-gray-700 text-lg mb-4">
                Non, mais nous aimerions bien qu'il existe.
              </p>
              <p className="text-gray-600 mb-4">
                Mais cela ne veut pas dire que vous ne pouvez pas trouver le <strong>lave-linge</strong> qui vous convient.
              </p>
              <p className="text-gray-600 mb-4">
                Dans ce guide, nous vous présentons quelques-uns des meilleurs <strong>lave-linge</strong> disponibles 
                et vous donnons des conseils sur la manière de choisir celui qui vous convient le mieux.
              </p>
              <p className="text-gray-700 font-medium">
                Alors, plongeons dans le vif du sujet. 👇
              </p>
            </div>
          </div>
          
          {/* Right Column - Visual Element */}
          <div className="bg-gradient-to-br from-blue-50 to-indigo-100 rounded-xl p-8 text-center">
            <div className="text-6xl mb-4">🏠</div>
            <h3 className="text-xl font-semibold text-gray-800 mb-2">
              Votre Maison, Notre Expertise
            </h3>
            <p className="text-gray-600">
              Découvrez les lave-linge qui durent et vous font économiser
            </p>
          </div>
        </div>
      </section>

      {/* Methodology Section with Colors */}
      <section className="py-8 bg-gradient-to-r from-blue-50 to-indigo-50 rounded-xl mb-8">
        <div className="max-w-4xl mx-auto px-6">
          <h2 className="text-2xl font-bold text-gray-900 mb-6 text-center">
            Notre Méthodologie
          </h2>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
            <div className="bg-white rounded-lg p-6 shadow-sm">
              <div className="flex items-center mb-4">
                <span className="text-2xl mr-3">📊</span>
                <h3 className="font-semibold text-lg text-blue-600">Tests Rigoureux</h3>
              </div>
              <p className="text-gray-600">
                Chaque lave-linge est évalué selon des critères stricts : réparabilité, 
                fiabilité, consommation d'énergie et durabilité.
              </p>
            </div>
            <div className="bg-white rounded-lg p-6 shadow-sm">
              <div className="flex items-center mb-4">
                <span className="text-2xl mr-3">🔍</span>
                <h3 className="font-semibold text-lg text-blue-600">Indépendance Totale</h3>
              </div>
              <p className="text-gray-600">
                Nos tests sont réalisés de manière indépendante. Nous pouvons toucher 
                une commission si vous achetez via nos liens.
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* Results Section */}
      <section className="mb-12">
        <Suspense fallback={
          <div className="text-center py-12">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
            <p className="mt-4 text-gray-600">Recherche en cours...</p>
          </div>
        }>
          <MachineResults query={searchParams.q} />
        </Suspense>
      </section>

      {/* CTA Section with Gradient */}
      {!searchParams.q && (
        <section className="py-12 bg-gradient-to-r from-blue-600 to-indigo-600 rounded-xl text-white">
          <div className="text-center">
            <h2 className="text-2xl font-bold mb-4">
              Prêt à trouver votre lave-linge idéal ?
            </h2>
            <p className="text-blue-100 mb-6 text-lg">
              Commencez votre recherche pour découvrir les meilleurs modèles 
              selon vos besoins et votre budget.
            </p>
            <div className="space-y-4">
              <p className="text-blue-200">
                Exemples de recherche : "Samsung", "plus réparable", "2025", "LG fiable"
              </p>
            </div>
          </div>
        </section>
      )}
    </div>
  );
}
