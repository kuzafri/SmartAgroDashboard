const express = require('express');
const router = express.Router();
const db = require('./db'); // Adjust the path to your database connection

// Function to fetch water pump count
router.get('/water-pump-count', async (req, res) => {
    try {
        const result = await db.query('SELECT COUNT(*) as count FROM water_pumps'); // Adjust the query as per your database
        res.json({ count: result[0].count });
    } catch (error) {
        console.error(error);
        res.status(500).send('Server Error');
    }
});

module.exports = router;