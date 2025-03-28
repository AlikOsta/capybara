
const InfiniteScrollModule = {
    settings: {
        isLoading: false,
        offset: 0,
        limit: 20,
        hasMore: true,
        loadThreshold: 70, 
        observerThreshold: 0.2, 
        animationDelay: 5, 
        loadingTimeout: null
    },

    elements: {
        productsContainer: null,
        loaderElement: null,
        endMessageElement: null,
        errorElement: null,
        backToTopButton: null,
        retryButton: null
    },

    init() {
        const { productsContainer, loaderElement, errorElement, retryButton } = this.elements;
        this.elements.productsContainer = document.getElementById('products-container');
        this.elements.loaderElement = document.getElementById('loader');
        this.elements.endMessageElement = document.getElementById('end-message');
        this.elements.errorElement = document.getElementById('error-message');
        this.elements.backToTopButton = document.getElementById('back-to-top');
        this.elements.retryButton = document.getElementById('retry-button');

        if (!this.elements.productsContainer) return;

        this.settings.offset = parseInt(this.elements.productsContainer.dataset.offset || '20', 10);
        this.settings.hasMore = this.elements.productsContainer.dataset.hasMore === 'true';

        this.initIntersectionObserver();
        this.initEventListeners();
    },

    initIntersectionObserver() {
        const { loaderElement } = this.elements;
        if (!loaderElement) return;

        const observer = new IntersectionObserver((entries) => {
            if (entries[0].isIntersecting && !this.settings.isLoading && this.settings.hasMore) {
                this.loadMoreProducts();
            }
        }, { threshold: this.settings.observerThreshold });

        observer.observe(loaderElement);
    },

    initEventListeners() {
        window.addEventListener('scroll', () => this.handleScroll());
        if (this.elements.retryButton) {
            this.elements.retryButton.addEventListener('click', () => {
                if (this.elements.errorElement) {
                    this.elements.errorElement.style.display = 'none';
                }
                this.loadMoreProducts();
            });
        }
    },

    handleScroll() {
        const scrollTop = window.pageYOffset || document.documentElement.scrollTop;
        const scrollHeight = document.documentElement.scrollHeight;
        const clientHeight = document.documentElement.clientHeight;
        const scrollPercentage = (scrollTop / (scrollHeight - clientHeight)) * 100;

        if (scrollPercentage >= this.settings.loadThreshold && !this.settings.isLoading && this.settings.hasMore) {
            clearTimeout(this.settings.loadingTimeout);
            this.settings.loadingTimeout = setTimeout(() => {
                this.loadMoreProducts();
            }, 100);
        }
    },

    loadMoreProducts() {
        if (this.settings.isLoading || !this.settings.hasMore) return;

        this.settings.isLoading = true;
        this.showLoader();

        const apiUrl = this.getApiUrl();
        if (!apiUrl) {
            this.hideLoader();
            this.settings.isLoading = false;
            return;
        }

        fetch(apiUrl)
            .then(response => {
                if (!response.ok) {
                    throw new Error('Ошибка загрузки данных');
                }
                return response.json();
            })
            .then(data => {
                if (data.html) {
                    this.appendNewProducts(data.html);
                    this.settings.offset = data.next_offset || this.settings.offset;
                    this.settings.hasMore = data.has_more;

                    if (!this.settings.hasMore && this.elements.endMessageElement) {
                        this.elements.endMessageElement.style.display = 'block';
                    }
                }
            })
            .catch(error => {
                console.error('Ошибка:', error);
                if (this.elements.errorElement) {
                    this.elements.errorElement.style.display = 'block';
                }
            })
            .finally(() => {
                this.hideLoader();
                this.settings.isLoading = false;
            });
    },

    getApiUrl() {
        const urlParams = new URLSearchParams(window.location.search);
        const params = new URLSearchParams();

        params.append('offset', this.settings.offset);
        params.append('limit', this.settings.limit);

        for (const [key, value] of urlParams.entries()) {
            if (key !== 'page') {
                params.append(key, value);
            }
        }

        const path = window.location.pathname;
        let apiUrl = null;

        if (path.includes('/category/')) {
            const categorySlug = path.split('/category/')[1].replace('/', '');
            apiUrl = `/api/category/${categorySlug}/products/?${params.toString()}`;
        } else if (path === '/' || path === '') {
            apiUrl = `/api/products/?${params.toString()}`;
        } else if (path.includes('/favorites/')) {
            apiUrl = `/api/favorites/?${params.toString()}`;
        }

        return apiUrl;
    },

    appendNewProducts(html) {
        const tempContainer = document.createElement('div');
        tempContainer.innerHTML = html;

        const newProductItems = tempContainer.querySelectorAll('.product-item');
        newProductItems.forEach((item, index) => {
            item.style.opacity = '0';
            item.style.transform = 'translateY(20px)';
            this.elements.productsContainer.appendChild(item);
            setTimeout(() => {
                item.style.transition = 'opacity 0.3s ease, transform 0.3s ease';
                item.style.opacity = '1';
                item.style.transform = 'translateY(0)';
            }, this.settings.animationDelay * (index + 1));
        });

        if (typeof window.initFavoriteButtons === 'function') {
            window.initFavoriteButtons();
        }
    },

    showLoader() {
        if (this.elements.loaderElement) {
            this.elements.loaderElement.style.display = 'block';
        }
    },

    hideLoader() {
        if (this.elements.loaderElement) {
            this.elements.loaderElement.style.display = 'none';
        }
    }
};

document.addEventListener('DOMContentLoaded', () => {
    InfiniteScrollModule.init();
});
