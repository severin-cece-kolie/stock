/*
 * Service Worker StockManager — stratégie volontairement prudente.
 *
 * IMPORTANT : cette application gère du stock et des ventes en temps
 * réel. On ne met JAMAIS en cache les pages de données (produits,
 * stock, ventes...) : afficher un stock périmé pourrait faire vendre
 * un produit qui n'est plus disponible. Seuls les fichiers statiques
 * (icônes, manifest) sont mis en cache, pour un chargement plus
 * rapide et l'installation "à l'écran d'accueil". Toute page vivante
 * est systématiquement rechargée depuis le réseau ; en l'absence de
 * réseau, une page "hors ligne" simple est affichée à la place.
 */

const CACHE_NAME = 'stockmanager-shell-v1';
const SHELL_ASSETS = [
    '/static/images/icons/icon-192.png',
    '/static/images/icons/icon-512.png',
    '/static/images/favicon.svg',
    '/manifest.json',
];

self.addEventListener('install', (event) => {
    event.waitUntil(
        caches.open(CACHE_NAME).then((cache) => cache.addAll(SHELL_ASSETS))
    );
    self.skipWaiting();
});

self.addEventListener('activate', (event) => {
    event.waitUntil(
        caches.keys().then((keys) =>
            Promise.all(keys.filter((k) => k !== CACHE_NAME).map((k) => caches.delete(k)))
        )
    );
    self.clients.claim();
});

self.addEventListener('fetch', (event) => {
    const { request } = event;

    // Navigation (chargement de page) : réseau en priorité, jamais de
    // page de données mise en cache. Si hors ligne, page de secours.
    if (request.mode === 'navigate') {
        event.respondWith(
            fetch(request).catch(() => caches.match('/hors-ligne/'))
        );
        return;
    }

    // Fichiers statiques du "shell" (icônes, manifest) : cache d'abord,
    // réseau en secours.
    if (SHELL_ASSETS.some((asset) => request.url.endsWith(asset))) {
        event.respondWith(
            caches.match(request).then((cached) => cached || fetch(request))
        );
        return;
    }

    // Tout le reste (données, formulaires...) : réseau uniquement,
    // aucune interception.
});
