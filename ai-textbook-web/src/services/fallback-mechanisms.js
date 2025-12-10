// ai-textbook-web/src/services/fallback-mechanisms.js

class FallbackMechanismsService {
  constructor() {
    this.fallbackStrategies = {
      retry: {
        enabled: true,
        maxAttempts: 3,
        baseDelay: 1000, // 1 second
        maxDelay: 10000, // 10 seconds
        backoffMultiplier: 2
      },
      cache: {
        enabled: true,
        ttl: 300000, // 5 minutes
        maxSize: 100 // max cached items
      },
      timeout: {
        enabled: true,
        defaultTimeout: 30000, // 30 seconds
        longRunningTimeout: 60000 // 60 seconds
      },
      circuitBreaker: {
        enabled: true,
        failureThreshold: 5, // failures before opening circuit
        resetTimeout: 60000, // 60 seconds before attempting reset
        successThreshold: 3 // successful calls to close circuit
      }
    };

    this.cache = new Map();
    this.circuitState = {
      isOpen: false,
      failureCount: 0,
      lastFailureTime: null,
      successCount: 0
    };
    this.requestQueue = []; // For handling requests when circuit is open
  }

  /**
   * Executes a function with fallback mechanisms
   * @param {Function} fn - Function to execute
   * @param {Object} options - Execution options
   * @returns {Promise} Result of the function execution
   */
  async executeWithFallback(fn, options = {}) {
    // Check circuit breaker first
    if (this.circuitState.isOpen) {
      const now = Date.now();
      if (now - this.circuitState.lastFailureTime > this.fallbackStrategies.circuitBreaker.resetTimeout) {
        // Attempt to reset circuit after timeout
        this.circuitState.isOpen = false;
        this.circuitState.failureCount = 0;
        this.circuitState.successCount = 0;
      } else {
        // Circuit is open, use fallback or queue request
        if (options.queueWhenOpen) {
          return this.queueRequest(fn, options);
        }
        throw new Error('Service temporarily unavailable - circuit breaker open');
      }
    }

    // Check cache first if enabled
    if (this.fallbackStrategies.cache.enabled && options.cacheKey) {
      const cachedResult = this.cache.get(options.cacheKey);
      if (cachedResult && Date.now() - cachedResult.timestamp < this.fallbackStrategies.cache.ttl) {
        return cachedResult.data;
      }
    }

    // Apply timeout
    const timeoutPromise = new Promise((_, reject) => {
      setTimeout(() => reject(new Error('Request timeout')),
        options.timeout || this.fallbackStrategies.timeout.defaultTimeout);
    });

    // Apply retry logic
    let lastError;
    const maxAttempts = options.maxAttempts || this.fallbackStrategies.retry.maxAttempts;

    for (let attempt = 0; attempt < maxAttempts; attempt++) {
      try {
        // Create a promise that races against timeout
        const operationPromise = Promise.resolve().then(() => fn(attempt));
        const result = await Promise.race([operationPromise, timeoutPromise]);

        // Success - update circuit state and cache
        this.updateCircuitState(true);

        if (this.fallbackStrategies.cache.enabled && options.cacheKey) {
          this.cache.set(options.cacheKey, {
            data: result,
            timestamp: Date.now()
          });

          // Clean up old entries if cache is too large
          if (this.cache.size > this.fallbackStrategies.cache.maxSize) {
            const oldestKey = this.cache.keys().next().value;
            this.cache.delete(oldestKey);
          }
        }

        return result;
      } catch (error) {
        lastError = error;

        // Update circuit state for failure
        this.updateCircuitState(false);

        // If this was the last attempt, break the loop
        if (attempt === maxAttempts - 1) {
          break;
        }

        // Calculate delay for next retry with exponential backoff
        const delay = Math.min(
          this.fallbackStrategies.retry.baseDelay * Math.pow(this.fallbackStrategies.retry.backoffMultiplier, attempt),
          this.fallbackStrategies.retry.maxDelay
        );

        // Wait before retrying
        await new Promise(resolve => setTimeout(resolve, delay));
      }
    }

    // All retries failed - throw the last error
    throw lastError;
  }

  /**
   * Updates circuit breaker state based on operation result
   * @param {boolean} success - Whether the operation was successful
   */
  updateCircuitState(success) {
    if (success) {
      this.circuitState.successCount++;
      this.circuitState.failureCount = Math.max(0, this.circuitState.failureCount - 1); // Reduce failure count on success

      // Close circuit if enough successes
      if (this.circuitState.successCount >= this.fallbackStrategies.circuitBreaker.successThreshold) {
        this.circuitState.isOpen = false;
        this.circuitState.successCount = 0;
        this.circuitState.failureCount = 0;
      }
    } else {
      this.circuitState.successCount = 0; // Reset success count on failure
      this.circuitState.failureCount++;
      this.circuitState.lastFailureTime = Date.now();

      // Open circuit if threshold reached
      if (this.circuitState.failureCount >= this.fallbackStrategies.circuitBreaker.failureThreshold) {
        this.circuitState.isOpen = true;
      }
    }
  }

  /**
   * Queues a request to be executed when circuit closes
   */
  async queueRequest(fn, options) {
    return new Promise((resolve, reject) => {
      this.requestQueue.push({ fn, options, resolve, reject });

      // Process queue when circuit closes
      const processQueue = () => {
        if (!this.circuitState.isOpen && this.requestQueue.length > 0) {
          const { fn: queuedFn, options: queuedOptions, resolve: queuedResolve, reject: queuedReject } = this.requestQueue.shift();

          this.executeWithFallback(queuedFn, queuedOptions)
            .then(queuedResolve)
            .catch(queuedReject);

          // Process next item in queue
          if (this.requestQueue.length > 0) {
            setTimeout(processQueue, 100);
          }
        }
      };

      // Try to process queue in a bit
      setTimeout(processQueue, 1000);
    });
  }

  /**
   * Security validation for inputs and responses
   */
  validateSecurity(input, context = {}) {
    const securityIssues = [];

    // Validate input for potential security issues
    if (input && typeof input === 'string') {
      // Check for potential XSS attempts
      if (this.containsXSS(input)) {
        securityIssues.push({
          type: 'xss_attempt',
          message: 'Input contains potential XSS attempt',
          severity: 'high'
        });
      }

      // Check for potential injection attempts
      if (this.containsInjection(input)) {
        securityIssues.push({
          type: 'injection_attempt',
          message: 'Input contains potential injection attempt',
          severity: 'high'
        });
      }

      // Check for overly long inputs (potential DoS)
      if (input.length > 10000) {
        securityIssues.push({
          type: 'potential_dos',
          message: 'Input length exceeds reasonable limit',
          severity: 'medium'
        });
      }
    }

    // Validate context for security issues
    if (context && typeof context === 'object') {
      // Check for sensitive data in context
      const sensitiveKeys = ['password', 'token', 'secret', 'key', 'auth', 'credential'];
      for (const [key, value] of Object.entries(context)) {
        if (sensitiveKeys.some(sensitive => key.toLowerCase().includes(sensitive))) {
          securityIssues.push({
            type: 'sensitive_data_exposure',
            message: `Potential sensitive data in context key: ${key}`,
            severity: 'high'
          });
        }
      }
    }

    return {
      isValid: securityIssues.length === 0,
      issues: securityIssues,
      sanitizedInput: this.sanitizeInput(input)
    };
  }

  /**
   * Checks if input contains potential XSS patterns
   */
  containsXSS(input) {
    const xssPatterns = [
      /<script\b[^<]*(?:(?!<\/script>)<[^<]*)*<\/script>/gi,
      /javascript:/gi,
      /on\w+\s*=/gi,
      /<iframe/gi,
      /<object/gi,
      /<embed/gi,
      /eval\(/gi,
      /expression\(/gi
    ];

    return xssPatterns.some(pattern => pattern.test(input));
  }

  /**
   * Checks if input contains potential injection patterns
   */
  containsInjection(input) {
    const injectionPatterns = [
      /('|;|--|\/\*|\*|union|select|insert|update|delete|drop|create|alter|exec|execute|system|shell)/gi
    ];

    return injectionPatterns.some(pattern => pattern.test(input));
  }

  /**
   * Sanitizes input to remove potentially dangerous content
   */
  sanitizeInput(input) {
    if (!input || typeof input !== 'string') {
      return input;
    }

    // Remove potential XSS content
    let sanitized = input
      .replace(/<script\b[^<]*(?:(?!<\/script>)<[^<]*)*<\/script>/gi, '')
      .replace(/javascript:/gi, '')
      .replace(/on\w+\s*=/gi, '')
      .replace(/<iframe/gi, '')
      .replace(/<object/gi, '')
      .replace(/<embed/gi, '');

    // Escape HTML characters
    sanitized = sanitized
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;')
      .replace(/'/g, '&#x27;');

    return sanitized;
  }

  /**
   * Applies fallback response when primary service fails
   */
  getFallbackResponse(originalQuery, error) {
    const fallbackResponses = [
      {
        response: "I'm currently experiencing technical difficulties. Please try your request again in a moment.",
        sources: [],
        confidence: 0.1
      },
      {
        response: "I'm having trouble processing your request right now. The system may be temporarily unavailable. Please try again later.",
        sources: [],
        confidence: 0.1
      },
      {
        response: "There was an issue with the AI service. I recommend checking the textbook content directly for the information you need.",
        sources: [
          {
            title: "Textbook Index",
            url: "/textbook/index",
            snippet: "Browse all textbook chapters and content"
          }
        ],
        confidence: 0.3
      }
    ];

    // Select a fallback response based on error type
    let fallback;
    if (error.message.includes('timeout')) {
      fallback = fallbackResponses[0];
    } else if (error.message.includes('circuit breaker')) {
      fallback = fallbackResponses[1];
    } else {
      fallback = fallbackResponses[2];
    }

    // Add error context to response
    fallback.response += ` (Error: ${error.message || 'Unknown error'})`;

    return fallback;
  }

  /**
   * Gets circuit breaker status
   */
  getCircuitStatus() {
    return {
      isOpen: this.circuitState.isOpen,
      failureCount: this.circuitState.failureCount,
      successCount: this.circuitState.successCount,
      lastFailureTime: this.circuitState.lastFailureTime,
      queueLength: this.requestQueue.length
    };
  }

  /**
   * Resets circuit breaker
   */
  resetCircuit() {
    this.circuitState = {
      isOpen: false,
      failureCount: 0,
      lastFailureTime: null,
      successCount: 0
    };
  }

  /**
   * Updates fallback strategies
   */
  updateStrategies(newStrategies) {
    this.fallbackStrategies = { ...this.fallbackStrategies, ...newStrategies };
  }

  /**
   * Clears the cache
   */
  clearCache() {
    this.cache.clear();
  }

  /**
   * Gets cache statistics
   */
  getCacheStats() {
    return {
      size: this.cache.size,
      maxSize: this.fallbackStrategies.cache.maxSize,
      hitRate: this.cache.size > 0 ? 0 : 0 // Would need to track hits/misses for real hit rate
    };
  }
}

export default FallbackMechanismsService;