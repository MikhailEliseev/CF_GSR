(function (window) {
  const STATUS_CONFIG = {
    completed: {
      alertClass: 'alert-success',
      iconClass: 'fas fa-check-circle',
      indicatorClass: 'status-completed-gsr'
    },
    success: {
      alertClass: 'alert-success',
      iconClass: 'fas fa-check-circle',
      indicatorClass: 'status-completed-gsr'
    },
    processing: {
      alertClass: 'alert-info',
      iconClass: 'fas fa-spinner fa-spin',
      indicatorClass: 'status-processing-gsr'
    },
    error: {
      alertClass: 'alert-danger',
      iconClass: 'fas fa-exclamation-circle',
      indicatorClass: 'status-error-gsr'
    },
    pending: {
      alertClass: 'alert-warning',
      iconClass: 'fas fa-clock',
      indicatorClass: 'status-pending-gsr'
    },
    info: {
      alertClass: 'alert-info',
      iconClass: 'fas fa-info-circle',
      indicatorClass: 'status-processing-gsr'
    }
  };

  function resolveConfig(status) {
    return STATUS_CONFIG[status] || STATUS_CONFIG.info;
  }

  function showStatus(elementId, status, message) {
    const target = typeof elementId === 'string' ? document.getElementById(elementId) : elementId;
    if (!target) {
      return;
    }

    const { alertClass, iconClass, indicatorClass } = resolveConfig(status);

    target.innerHTML = `
      <div class="alert ${alertClass} status-alert d-flex align-items-center mb-0">
        <span class="status-indicator-gsr ${indicatorClass} me-2"></span>
        <i class="${iconClass} me-2"></i>
        <span>${message}</span>
      </div>
    `;
  }

  function enableStep(stepId) {
    const step = document.getElementById(stepId);
    if (!step) {
      return;
    }
    step.classList.remove('step-disabled');
    step.classList.add('step-enabled');
  }

  function disableStep(stepId) {
    const step = document.getElementById(stepId);
    if (!step) {
      return;
    }
    step.classList.add('step-disabled');
    step.classList.remove('step-enabled');
    step.classList.remove('step-active');
  }

  function activateStep(stepId, options) {
    const strategy = Object.assign({ exclusive: false }, options);
    const step = document.getElementById(stepId);
    if (!step) {
      return;
    }

    if (strategy.exclusive) {
      document.querySelectorAll('.progress-step').forEach((el) => {
        el.classList.remove('step-active');
      });
    }

    step.classList.add('step-active');
  }

  function resetStatus(elementId) {
    const target = typeof elementId === 'string' ? document.getElementById(elementId) : elementId;
    if (target) {
      target.innerHTML = '';
    }
  }

  window.GSRPipeline = {
    showStatus,
    enableStep,
    disableStep,
    activateStep,
    resetStatus
  };
})(window);
