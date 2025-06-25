const express = require('express');
const {
  createExpense,
  getExpenses,
  getExpensesByTrip,
  getAIInsights,
  updateExpense,
  deleteExpense
} = require('../controllers/expenseController');
const authMiddleware = require('../utils/authMiddleware');

const router = express.Router();

router.use(authMiddleware);

router.post('/', createExpense);
router.get('/', getExpenses);
router.get('/trip/:tripId', getExpensesByTrip);
router.post('/ai-insights', getAIInsights);
router.put('/:id', updateExpense);
router.delete('/:id', deleteExpense);

module.exports = router;
