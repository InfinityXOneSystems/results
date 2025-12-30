#!/usr/bin/env node

/**
 * Results API Server
 * RESTful API for accessing and managing autonomous results
 */

import express from 'express';
import cors from 'cors';
import helmet from 'helmet';
import { AutonomousResultsAgent } from './autonomous-results-agent';

const app = express();
const PORT = process.env.PORT || 8081;

// Middleware
app.use(helmet());
app.use(cors());
app.use(express.json({ limit: '50mb' }));
app.use(express.urlencoded({ extended: true }));

// Initialize the results agent
const resultsAgent = new AutonomousResultsAgent();

// Start the agent
resultsAgent.start().catch(console.error);

// Routes

// Health check
app.get('/health', (req, res) => {
  res.json({
    status: 'healthy',
    timestamp: new Date().toISOString(),
    agent: 'Autonomous Results Agent',
    version: '1.0.0'
  });
});

// Get system statistics
app.get('/api/statistics', async (req, res) => {
  try {
    const stats = await resultsAgent.getStatistics();
    res.json(stats);
  } catch (error) {
    const err = error as Error;
    res.status(500).json({ error: err.message });
  }
});

// Search results
app.get('/api/search', async (req, res) => {
  try {
    const query = {
      text: req.query.q as string,
      type: req.query.type as string,
      tags: req.query.tags ? (req.query.tags as string).split(',') : undefined,
      dateRange: req.query.start && req.query.end ? {
        start: new Date(req.query.start as string),
        end: new Date(req.query.end as string)
      } : undefined,
      quality: req.query.minQuality && req.query.maxQuality ? {
        min: parseInt(req.query.minQuality as string),
        max: parseInt(req.query.maxQuality as string)
      } : undefined
    };

    const results = await resultsAgent.search(query);
    res.json(results);
  } catch (error) {
    const err = error as Error;
    res.status(500).json({ error: err.message });
  }
});

// Get results by category
app.get('/api/categories/:category', async (req, res) => {
  try {
    const category = req.params.category;
    const limit = parseInt(req.query.limit as string) || 50;
    const offset = parseInt(req.query.offset as string) || 0;

    // This would need to be implemented in the agent
    res.json({ category, limit, offset, message: 'Category endpoint not yet implemented' });
  } catch (error) {
    const err = error as Error;
    res.status(500).json({ error: err.message });
  }
});

// Get specific result
app.get('/api/results/:id', async (req, res) => {
  try {
    const id = req.params.id;
    // This would need to be implemented in the agent
    res.json({ id, message: 'Result details endpoint not yet implemented' });
  } catch (error) {
    const err = error as Error;
    res.status(500).json({ error: err.message });
  }
});

// Get analytics for category
app.get('/api/analytics/:category', async (req, res) => {
  try {
    const category = req.params.category;
    const timeRange = req.query.range as string || '30d';

    // This would need to be implemented in the agent
    res.json({
      category,
      timeRange,
      message: 'Analytics endpoint not yet implemented'
    });
  } catch (error) {
    const err = error as Error;
    res.status(500).json({ error: err.message });
  }
});

// Manual ingestion endpoint
app.post('/api/ingest', async (req, res) => {
  try {
    const { type, data, source } = req.body;

    if (!type || !data) {
      return res.status(400).json({ error: 'Missing required fields: type, data' });
    }

    // Create a temporary file for ingestion
    const tempFile = `/tmp/result_${Date.now()}_${Math.random()}.json`;
    require('fs').writeFileSync(tempFile, JSON.stringify(data));

    // Trigger ingestion (this would need to be implemented)
    res.json({
      message: 'Ingestion triggered',
      type,
      source: source || 'api',
      tempFile
    });
  } catch (error) {
    const err = error as Error;
    res.status(500).json({ error: err.message });
  }
});

// Get agent status
app.get('/api/status', async (req, res) => {
  try {
    // This would need to be implemented in the agent
    res.json({
      agent: 'Autonomous Results Agent',
      status: 'running',
      uptime: process.uptime(),
      memory: process.memoryUsage(),
      timestamp: new Date().toISOString()
    });
  } catch (error) {
    const err = error as Error;
    res.status(500).json({ error: err.message });
  }
});

// Error handling middleware
app.use((error: any, req: express.Request, res: express.Response, next: express.NextFunction) => {
  console.error('API Error:', error);
  res.status(500).json({
    error: 'Internal server error',
    message: error.message,
    timestamp: new Date().toISOString()
  });
});

// 404 handler
app.use((req, res) => {
  res.status(404).json({
    error: 'Not found',
    path: req.path,
    method: req.method,
    timestamp: new Date().toISOString()
  });
});

// Graceful shutdown
process.on('SIGINT', async () => {
  console.log('Received SIGINT, shutting down gracefully...');
  await resultsAgent.stop();
  process.exit(0);
});

process.on('SIGTERM', async () => {
  console.log('Received SIGTERM, shutting down gracefully...');
  await resultsAgent.stop();
  process.exit(0);
});

// Start server
app.listen(PORT, () => {
  console.log(`🚀 Results API Server running on port ${PORT}`);
  console.log(`📊 Health check: http://localhost:${PORT}/health`);
  console.log(`📈 Statistics: http://localhost:${PORT}/api/statistics`);
  console.log(`🔍 Search: http://localhost:${PORT}/api/search?q=query`);
});

export default app;