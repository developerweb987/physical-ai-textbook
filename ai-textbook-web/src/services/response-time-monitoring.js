// ai-textbook-web/src/services/response-time-monitoring.js

class ResponseTimeMonitoringService {
  constructor() {
    this.metrics = {
      responseTimes: [],
      averageResponseTime: 0,
      p95ResponseTime: 0,
      p99ResponseTime: 0,
      totalRequests: 0,
      failedRequests: 0,
      throughput: 0 // requests per minute
    };

    this.performanceThresholds = {
      warning: 2000, // 2 seconds
      error: 5000,   // 5 seconds
      maxAcceptable: 10000 // 10 seconds
    };

    this.startTime = new Date();
    this.requestHistory = [];
  }

  /**
   * Starts timing a request
   * @returns {string} Request ID for tracking
   */
  startTiming() {
    const requestId = `req_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
    this.requestHistory.push({
      id: requestId,
      startTime: Date.now(),
      endTime: null,
      duration: null,
      status: 'pending'
    });
    return requestId;
  }

  /**
   * Ends timing for a request and records metrics
   * @param {string} requestId - Request ID from startTiming
   * @param {boolean} success - Whether the request was successful
   * @param {Object} additionalData - Additional data to record
   */
  endTiming(requestId, success = true, additionalData = {}) {
    const request = this.requestHistory.find(req => req.id === requestId);
    if (!request) {
      console.warn(`Request ${requestId} not found in history`);
      return;
    }

    const endTime = Date.now();
    const duration = endTime - request.startTime;

    request.endTime = endTime;
    request.duration = duration;
    request.status = success ? 'success' : 'failed';
    request.additionalData = additionalData;

    // Update metrics
    this.metrics.responseTimes.push(duration);
    if (!success) {
      this.metrics.failedRequests++;
    }
    this.metrics.totalRequests++;

    // Calculate rolling averages (keep only last 1000 measurements)
    if (this.metrics.responseTimes.length > 1000) {
      this.metrics.responseTimes = this.metrics.responseTimes.slice(-1000);
    }

    this.updateMetrics();
  }

  /**
   * Updates calculated metrics
   */
  updateMetrics() {
    if (this.metrics.responseTimes.length === 0) {
      this.metrics.averageResponseTime = 0;
      this.metrics.p95ResponseTime = 0;
      this.metrics.p99ResponseTime = 0;
      return;
    }

    // Calculate average response time
    const sum = this.metrics.responseTimes.reduce((a, b) => a + b, 0);
    this.metrics.averageResponseTime = Math.round(sum / this.metrics.responseTimes.length);

    // Calculate percentiles
    const sortedTimes = [...this.metrics.responseTimes].sort((a, b) => a - b);
    const length = sortedTimes.length;

    // P95 (95th percentile)
    const p95Index = Math.floor(length * 0.95);
    this.metrics.p95ResponseTime = sortedTimes[Math.min(p95Index, length - 1)] || 0;

    // P99 (99th percentile)
    const p99Index = Math.floor(length * 0.99);
    this.metrics.p99ResponseTime = sortedTimes[Math.min(p99Index, length - 1)] || 0;

    // Calculate throughput (requests per minute)
    const timeElapsed = (Date.now() - this.startTime) / 60000; // in minutes
    this.metrics.throughput = timeElapsed > 0 ?
      Math.round(this.metrics.totalRequests / timeElapsed) : 0;
  }

  /**
   * Validates response time against thresholds
   * @param {number} responseTime - Response time in milliseconds
   * @returns {Object} Validation result
   */
  validateResponseTime(responseTime) {
    const result = {
      isValid: true,
      level: 'success', // success, warning, error
      message: 'Response time is acceptable',
      threshold: null
    };

    if (responseTime > this.performanceThresholds.maxAcceptable) {
      result.isValid = false;
      result.level = 'error';
      result.message = `Response time (${responseTime}ms) exceeds maximum acceptable time (${this.performanceThresholds.maxAcceptable}ms)`;
      result.threshold = 'maxAcceptable';
    } else if (responseTime > this.performanceThresholds.error) {
      result.isValid = false;
      result.level = 'error';
      result.message = `Response time (${responseTime}ms) exceeds error threshold (${this.performanceThresholds.error}ms)`;
      result.threshold = 'error';
    } else if (responseTime > this.performanceThresholds.warning) {
      result.isValid = true; // Still valid but with warning
      result.level = 'warning';
      result.message = `Response time (${responseTime}ms) exceeds warning threshold (${this.performanceThresholds.warning}ms)`;
      result.threshold = 'warning';
    }

    return result;
  }

  /**
   * Gets current performance metrics
   * @returns {Object} Performance metrics
   */
  getMetrics() {
    return { ...this.metrics };
  }

  /**
   * Gets performance report with recommendations
   * @returns {Object} Performance report
   */
  getPerformanceReport() {
    const metrics = this.getMetrics();

    const report = {
      summary: {
        totalRequests: metrics.totalRequests,
        failedRequests: metrics.failedRequests,
        successRate: metrics.totalRequests > 0 ?
          ((metrics.totalRequests - metrics.failedRequests) / metrics.totalRequests * 100).toFixed(2) : 100,
        throughput: metrics.throughput,
        averageResponseTime: metrics.averageResponseTime,
        p95ResponseTime: metrics.p95ResponseTime,
        p99ResponseTime: metrics.p99ResponseTime
      },
      recommendations: [],
      status: 'healthy' // healthy, warning, critical
    };

    // Generate recommendations based on metrics
    if (metrics.averageResponseTime > this.performanceThresholds.warning) {
      report.recommendations.push('Average response time is high. Consider optimizing backend processing or adding caching.');
    }

    if (metrics.p95ResponseTime > this.performanceThresholds.error) {
      report.recommendations.push('95th percentile response time exceeds error threshold. Investigate slow queries or processing bottlenecks.');
    }

    if (metrics.failedRequests > 0) {
      const failureRate = (metrics.failedRequests / metrics.totalRequests * 100).toFixed(2);
      if (failureRate > 5) { // More than 5% failure rate
        report.recommendations.push('High failure rate detected. Check backend health and error logs.');
        report.status = 'critical';
      } else if (failureRate > 1) { // More than 1% failure rate
        report.recommendations.push('Failure rate is above 1%. Monitor backend health.');
        report.status = 'warning';
      }
    }

    if (metrics.throughput === 0 && metrics.totalRequests > 0) {
      report.recommendations.push('Throughput is 0, which may indicate an issue with time calculation period.');
    }

    // Determine overall status
    if (report.status === 'critical') {
      // Already set
    } else if (report.recommendations.length > 0) {
      report.status = 'warning';
    }

    return report;
  }

  /**
   * Resets all metrics
   */
  resetMetrics() {
    this.metrics = {
      responseTimes: [],
      averageResponseTime: 0,
      p95ResponseTime: 0,
      p99ResponseTime: 0,
      totalRequests: 0,
      failedRequests: 0,
      throughput: 0
    };
    this.requestHistory = [];
    this.startTime = new Date();
  }

  /**
   * Gets detailed request history (last N requests)
   * @param {number} limit - Number of requests to return (default 50)
   * @returns {Array} Request history
   */
  getRequestHistory(limit = 50) {
    return this.requestHistory.slice(-limit).map(req => ({
      id: req.id,
      duration: req.duration,
      status: req.status,
      timestamp: req.startTime ? new Date(req.startTime) : null,
      ...req.additionalData
    }));
  }

  /**
   * Sets new performance thresholds
   * @param {Object} thresholds - New threshold values
   */
  setPerformanceThresholds(thresholds) {
    this.performanceThresholds = { ...this.performanceThresholds, ...thresholds };
  }

  /**
   * Monitors a function execution time
   * @param {Function} fn - Function to monitor
   * @param {string} operationName - Name of the operation being monitored
   * @returns {Promise} Result of the function with timing data
   */
  async monitorFunction(fn, operationName = 'unknown') {
    const requestId = this.startTiming();

    try {
      const result = await fn();
      this.endTiming(requestId, true, { operation: operationName });
      return result;
    } catch (error) {
      this.endTiming(requestId, false, {
        operation: operationName,
        error: error.message
      });
      throw error;
    }
  }

  /**
   * Creates a monitored fetch wrapper
   * @param {string} url - URL to fetch
   * @param {Object} options - Fetch options
   * @param {string} operationName - Name of the operation
   * @returns {Promise} Fetch result with timing data
   */
  async monitoredFetch(url, options = {}, operationName = 'api_call') {
    const requestId = this.startTiming();

    try {
      const response = await fetch(url, options);
      const success = response.ok;
      this.endTiming(requestId, success, {
        operation: operationName,
        url,
        status: response.status
      });
      return response;
    } catch (error) {
      this.endTiming(requestId, false, {
        operation: operationName,
        url,
        error: error.message
      });
      throw error;
    }
  }
}

export default ResponseTimeMonitoringService;