const Expense = require('../models/Expense');
const Trip = require('../models/Trip');
const axios = require('axios');

const createExpense = async (req, res) => {
  try {
    const { tripId, description, amount, category, date } = req.body;
    
    // Verify trip belongs to user
    const trip = await Trip.findOne({ _id: tripId, user: req.user._id });
    if (!trip) {
      return res.status(404).json({ message: 'Trip not found' });
    }

    const expense = new Expense({
      user: req.user._id,
      trip: tripId,
      description,
      amount,
      category,
      date
    });

    await expense.save();
    res.status(201).json(expense);
  } catch (error) {
    res.status(500).json({ message: 'Server error', error: error.message });
  }
};

const getExpenses = async (req, res) => {
  try {
    const expenses = await Expense.find({ user: req.user._id })
      .populate('trip', 'destination')
      .sort({ date: -1 });
    res.json(expenses);
  } catch (error) {
    res.status(500).json({ message: 'Server error', error: error.message });
  }
};

const getExpensesByTrip = async (req, res) => {
  try {
    const { tripId } = req.params;
    
    // Verify trip belongs to user
    const trip = await Trip.findOne({ _id: tripId, user: req.user._id });
    if (!trip) {
      return res.status(404).json({ message: 'Trip not found' });
    }

    const expenses = await Expense.find({ trip: tripId, user: req.user._id })
      .sort({ date: -1 });
    res.json(expenses);
  } catch (error) {
    res.status(500).json({ message: 'Server error', error: error.message });
  }
};

const getAIInsights = async (req, res) => {
  try {
    const { tripId } = req.body;
    
    // Verify trip belongs to user
    const trip = await Trip.findOne({ _id: tripId, user: req.user._id });
    if (!trip) {
      return res.status(404).json({ message: 'Trip not found' });
    }

    // Get expenses for this trip
    const expenses = await Expense.find({ trip: tripId, user: req.user._id });
    
    // Prepare data for ML model
    const expenseData = expenses.map(expense => ({
      amount: expense.amount,
      category: expense.category,
      date: expense.date
    }));

    try {
      // Call ML service
      const mlResponse = await axios.post(`${process.env.ML_SERVICE_URL}/predict`, {
        expenses: expenseData,
        budget: trip.budget,
        trip_duration: Math.ceil((new Date(trip.endDate) - new Date(trip.startDate)) / (1000 * 60 * 60 * 24))
      });

      res.json(mlResponse.data);
    } catch (mlError) {
      // Fallback to basic analysis if ML service is unavailable
      const totalSpent = expenses.reduce((sum, expense) => sum + expense.amount, 0);
      const remainingBudget = trip.budget - totalSpent;
      const averageDaily = totalSpent / Math.max(1, expenses.length);
      
      res.json({
        predicted_spending: totalSpent * 1.2, // Simple prediction
        budget_status: remainingBudget > 0 ? 'on_track' : 'over_budget',
        recommendations: [
          remainingBudget < 0 ? 'You are over budget. Consider reducing expenses.' : 'You are within budget. Keep tracking!',
          `Your average daily spending is $${averageDaily.toFixed(2)}`,
          'Try to categorize expenses for better insights'
        ]
      });
    }
  } catch (error) {
    res.status(500).json({ message: 'Server error', error: error.message });
  }
};

const updateExpense = async (req, res) => {
  try {
    const expense = await Expense.findOneAndUpdate(
      { _id: req.params.id, user: req.user._id },
      req.body,
      { new: true }
    );

    if (!expense) {
      return res.status(404).json({ message: 'Expense not found' });
    }

    res.json(expense);
  } catch (error) {
    res.status(500).json({ message: 'Server error', error: error.message });
  }
};

const deleteExpense = async (req, res) => {
  try {
    const expense = await Expense.findOneAndDelete({ _id: req.params.id, user: req.user._id });

    if (!expense) {
      return res.status(404).json({ message: 'Expense not found' });
    }

    res.json({ message: 'Expense deleted successfully' });
  } catch (error) {
    res.status(500).json({ message: 'Server error', error: error.message });
  }
};

module.exports = {
  createExpense,
  getExpenses,
  getExpensesByTrip,
  getAIInsights,
  updateExpense,
  deleteExpense
};
