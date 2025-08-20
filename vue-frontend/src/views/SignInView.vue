<template>
  <div class="signin-container">
    <div class="signin-card">
      <!-- Header -->
      <div class="signin-header">
        <h1>Enlingo</h1>
        <h2>Welcome back</h2>
      </div>

      <!-- Divider -->
      <div class="divider"></div>

      <!-- Sign In Form -->
      <form @submit.prevent="handleSignIn" class="signin-form">
        <!-- Username Field -->
        <div class="form-group">
          <input
            v-model="form.username"
            type="text"
            required
            placeholder="Username"
            :class="{ 'error-input': errors.username }"
            @input="clearError('username')"
          >
          <span v-if="errors.username" class="error-message">{{ errors.username }}</span>
        </div>

        <!-- Password Field -->
        <div class="form-group">
          <input
            v-model="form.password"
            type="password"
            required
            placeholder="Password"
            :class="{ 'error-input': errors.password }"
            @input="clearError('password')"
          >
          <span v-if="errors.password" class="error-message">{{ errors.password }}</span>
        </div>

        <!-- Submit Button -->
        <button
          type="submit"
          class="signin-button"
          :disabled="loading"
          :class="{ 'loading': loading }"
        >
          <span v-if="!loading">Sign in</span>
          <span v-else>Signing in...</span>
        </button>
      </form>

      <!-- Error Message -->
      <div v-if="generalError" class="general-error">
        {{ generalError }}
      </div>

      <!-- Sign Up Link -->
      <div class="signup-link">
        <p>New to Enlingo? <router-link to="/signup">Sign up</router-link></p>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'SignIn',
  data() {
    return {
      form: {
        username: '',
        password: ''
      },
      errors: {
        username: '',
        password: ''
      },
      generalError: '',
      loading: false
    }
  },
  methods: {
    validateForm() {
      let isValid = true
      this.clearAllErrors()

      if (!this.form.username.trim()) {
        this.errors.username = 'Username is required'
        isValid = false
      }

      if (!this.form.password) {
        this.errors.password = 'Password is required'
        isValid = false
      }

      return isValid
    },

    clearError(field) {
      this.errors[field] = ''
      this.generalError = ''
    },

    clearAllErrors() {
      this.errors = {
        username: '',
        password: ''
      }
      this.generalError = ''
    },

    async handleSignIn() {
      if (!this.validateForm()) {
        return
      }

      this.loading = true
      this.generalError = ''

      try {
        const response = await fetch('/api/auth/login', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            name: this.form.username,
            password: this.form.password
          })
        })

        const data = await response.json()

        if (response.ok) {
          // Login successful
          localStorage.setItem('authToken', data.token || 'dummy-token')
          localStorage.setItem('user', JSON.stringify(data.user || { name: this.form.username }))
          this.$router.push('/dashboard')
        } else {
          this.generalError = data.error || 'Invalid credentials. Please try again.'
        }
      } catch (error) {
        console.error('Login error:', error)
        this.generalError = 'Network error. Please try again.'
      } finally {
        this.loading = false
      }
    }
  }
}
</script>

<style scoped>
.signin-container {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  padding: 20px;
}

.signin-card {
  background: white;
  padding: 2.5rem;
  border-radius: 12px;
  box-shadow: 0 10px 25px rgba(0, 0, 0, 0.1);
  width: 100%;
  max-width: 400px;
}

.signin-header {
  text-align: center;
  margin-bottom: 1.5rem;
}

.signin-header h1 {
  color: #333;
  font-size: 2rem;
  font-weight: bold;
  margin-bottom: 0.5rem;
}

.signin-header h2 {
  color: #666;
  font-size: 1.25rem;
  font-weight: normal;
  margin: 0;
}

.divider {
  height: 1px;
  background: #e1e5e9;
  margin: 1.5rem 0;
}

.signin-form {
  margin-bottom: 1.5rem;
}

.form-group {
  margin-bottom: 1.5rem;
}

.form-group input {
  width: 100%;
  padding: 0.75rem;
  border: 2px solid #e1e5e9;
  border-radius: 6px;
  font-size: 1rem;
  transition: border-color 0.3s ease;
  box-sizing: border-box;
  background: #f8f9fa;
}

.form-group input:focus {
  outline: none;
  border-color: #667eea;
  background: white;
}

.form-group input::placeholder {
  color: #888;
}

.form-group input.error-input {
  border-color: #e74c3c;
  background: #fee;
}

.error-message {
  color: #e74c3c;
  font-size: 0.875rem;
  margin-top: 0.25rem;
  display: block;
}

.signin-button {
  width: 100%;
  padding: 0.75rem;
  background: #333;
  color: white;
  border: none;
  border-radius: 6px;
  font-size: 1rem;
  font-weight: 600;
  cursor: pointer;
  transition: background-color 0.3s ease;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.signin-button:hover:not(:disabled) {
  background: #555;
}

.signin-button:disabled {
  background: #95a5a6;
  cursor: not-allowed;
}

.signin-button.loading {
  background: #95a5a6;
}

.general-error {
  background: #fee;
  border: 1px solid #fcc;
  color: #c33;
  padding: 0.75rem;
  border-radius: 6px;
  margin-bottom: 1rem;
  text-align: center;
  font-size: 0.875rem;
}

.signup-link {
  text-align: center;
  color: #666;
  font-size: 0.9rem;
}

.signup-link a {
  color: #667eea;
  text-decoration: none;
  font-weight: 500;
}

.signup-link a:hover {
  text-decoration: underline;
}

/* Responsive design */
@media (max-width: 480px) {
  .signin-card {
    padding: 1.5rem;
    margin: 1rem;
  }
  
  .signin-header h1 {
    font-size: 1.75rem;
  }
  
  .signin-header h2 {
    font-size: 1.1rem;
  }
  
  .form-group input {
    padding: 0.625rem;
  }
  
  .signin-button {
    padding: 0.625rem;
  }
}
</style>