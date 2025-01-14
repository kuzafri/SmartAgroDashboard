export const ProductService = {
    getProductsData() {
        return [
            {
                id: '1000',
                code: 'org_tomato_1',
                name: 'Organic Tomatoes',
                description: 'Fresh organic tomatoes grown locally',
                image: 'tomatoes.jpg',
                price: 4.99,
                category: 'Vegetables',
                quantity: 150,
                unit: 'lbs',
                inventoryStatus: 'INSTOCK',
                harvestDate: '2024-03-15',
                rating: 5
            },
            {
                id: '1001',
                code: 'org_lettuce_1',
                name: 'Organic Lettuce',
                description: 'Crisp hydroponic lettuce',
                image: 'lettuce.jpg',
                price: 3.50,
                category: 'Vegetables',
                quantity: 75,
                unit: 'heads',
                inventoryStatus: 'INSTOCK',
                harvestDate: '2024-03-18',
                rating: 4
            },
            {
                id: '1002',
                code: 'frsh_eggs_1',
                name: 'Farm Fresh Eggs',
                description: 'Free-range organic eggs',
                image: 'eggs.jpg',
                price: 5.99,
                category: 'Dairy & Eggs',
                quantity: 200,
                unit: 'dozen',
                inventoryStatus: 'LOWSTOCK',
                harvestDate: '2024-03-19',
                rating: 5
            },
            {
                id: '1003',
                code: 'org_apples_1',
                name: 'Organic Apples',
                description: 'Sweet and crisp apples',
                image: 'apples.jpg',
                price: 2.99,
                category: 'Fruits',
                quantity: 300,
                unit: 'lbs',
                inventoryStatus: 'INSTOCK',
                harvestDate: '2024-03-10',
                rating: 4
            },
            {
                id: '1004',
                code: 'raw_honey_1',
                name: 'Raw Honey',
                description: 'Pure unfiltered honey',
                image: 'honey.jpg',
                price: 8.99,
                category: 'Specialty',
                quantity: 50,
                unit: 'jars',
                inventoryStatus: 'LOWSTOCK',
                harvestDate: '2024-02-15',
                rating: 5
            }
        ];
    },

    getProductsWithOrdersData() {
        return [
            {
                id: '1000',
                code: 'org_tomato_1',
                name: 'Organic Tomatoes',
                description: 'Fresh organic tomatoes grown locally',
                image: 'tomatoes.jpg',
                price: 4.99,
                category: 'Vegetables',
                quantity: 150,
                unit: 'lbs',
                inventoryStatus: 'INSTOCK',
                harvestDate: '2024-03-15',
                rating: 5,
                orders: [
                    {
                        id: '1000-0',
                        productCode: 'org_tomato_1',
                        date: '2024-03-16',
                        amount: 49.90,
                        quantity: 10,
                        customer: 'Local Market Co-op',
                        status: 'DELIVERED'
                    },
                    {
                        id: '1000-1',
                        productCode: 'org_tomato_1',
                        date: '2024-03-17',
                        amount: 24.95,
                        quantity: 5,
                        customer: 'Farm to Table Restaurant',
                        status: 'PENDING'
                    }
                ]
            },
            {
                id: '1001',
                code: 'org_lettuce_1',
                name: 'Organic Lettuce',
                description: 'Crisp hydroponic lettuce',
                image: 'lettuce.jpg',
                price: 3.50,
                category: 'Vegetables',
                quantity: 75,
                unit: 'heads',
                inventoryStatus: 'INSTOCK',
                harvestDate: '2024-03-18',
                rating: 4,
                orders: [
                    {
                        id: '1001-0',
                        productCode: 'org_lettuce_1',
                        date: '2024-03-18',
                        amount: 35.00,
                        quantity: 10,
                        customer: 'Green Grocers',
                        status: 'PENDING'
                    }
                ]
            }
        ];
    },

    getProductsMini() {
        return Promise.resolve(this.getProductsData().slice(0, 5));
    },

    getProductsSmall() {
        return Promise.resolve(this.getProductsData().slice(0, 10));
    },

    getProducts() {
        return Promise.resolve(this.getProductsData());
    },

    getProductsWithOrdersSmall() {
        return Promise.resolve(this.getProductsWithOrdersData().slice(0, 10));
    },

    getProductsWithOrders() {
        return Promise.resolve(this.getProductsWithOrdersData());
    },

    async getProductsFromDB() {
        const response = await fetch('http://your-flask-backend-url/data'); // Adjust the URL as needed
        if (!response.ok) {
            throw new Error('Failed to fetch products');
        }
        return await response.json();
    }
};
