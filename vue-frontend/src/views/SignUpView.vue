<template>
  <div class="signup-container">
    <div class="signup-card">
      <!-- Header -->
      <div class="signup-header">
        <h1>Enlingo</h1>
        <h2>Welcome</h2>
      </div>

      <!-- Sign Up Form -->
      <form @submit.prevent="handleSignUp" class="signup-form">
        <!-- Username Field -->
        <div class="form-group">
          <label for="username">Username</label>
          <input
            id="username"
            v-model="form.username"
            type="text"
            required
            placeholder="Enter your username"
            :class="{ 'error-input': errors.username }"
            @input="clearError('username')"
          >
          <span v-if="errors.username" class="error-message">{{ errors.username }}</span>
        </div>

        <!-- Password Field -->
        <div class="form-group">
          <label for="password">Password</label>
          <input
            id="password"
            v-model="form.password"
            type="password"
            required
            placeholder="Enter your password"
            :class="{ 'error-input': errors.password }"
            @input="clearError('password')"
          >
          <span v-if="errors.password" class="error-message">{{ errors.password }}</span>
        </div>

        <!-- Confirm Password Field -->
        <div class="form-group">
          <label for="confirmPassword">Confirm Password</label>
          <input
            id="confirmPassword"
            v-model="form.confirmPassword"
            type="password"
            required
            placeholder="Confirm your password"
            :class="{ 'error-input': errors.confirmPassword }"
            @input="clearError('confirmPassword')"
          >
          <span v-if="errors.confirmPassword" class="error-message">{{ errors.confirmPassword }}</span>
        </div>

        <!-- Submit Button -->
        <button
          type="submit"
          class="signup-button"
          :disabled="loading"
          :class="{ 'loading': loading }"
        >
          <span v-if="!loading">Sign up</span>
          <span v-else>Signing up...</span>
        </button>
      </form>

      <!-- Error Message -->
      <div v-if="generalError" class="general-error">
        {{ generalError }}
      </div>

      <!-- Sign In Link -->
      <div class="signin-link">
        <p>Already have an account? <router-link to="/signin">Sign in</router-link></p>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'SignUp',
  data() {
    return {
      form: {
        username: '',
        password: '',
        confirmPassword: ''
      },
      errors: {
        username: '',
        password: '',
        confirmPassword: ''
      },
      generalError: '',
      loading: false
    }
  },
  methods: {
    validateForm() {
      let isValid = true
      
      // Clear previous errors
      this.clearAllErrors()

      // Validate username
      if (!this.form.username.trim()) {
        this.errors.username = 'Username is required'
        isValid = false
      } else if (this.form.username.length < 3) {
        this.errors.username = 'Username must be at least 3 characters'
        isValid = false
      }

      // Validate password
      if (!this.form.password) {
        this.errors.password = 'Password is required'
        isValid = false
      } else if (this.form.password.length < 6) {
        this.errors.password = 'Password must be at least 6 characters'
        isValid = false
      }

      // Validate confirm password
      if (!this.form.confirmPassword) {
        this.errors.confirmPassword = 'Please confirm your password'
        isValid = false
      } else if (this.form.password !== this.form.confirmPassword) {
        this.errors.confirmPassword = 'Passwords do not match'
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
        password: '',
        confirmPassword: ''
      }
      this.generalError = ''
    },

    async handleSignUp() {
      // Validate form
      if (!this.validateForm()) {
        return
      }

      this.loading = true
      this.generalError = ''

      try {
        const response = await fetch('/api/auth/register', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            name: this.form.username,
            password: this.form.password,
            confirm_password: this.form.confirmPassword
          })
        })

        const data = await response.json()

        if (response.ok) {
          // Registration successful
          console.log('Registration successful:', data)
          
          // Store user data and token
          localStorage.setItem('authToken', data.token || 'dummy-token')
          localStorage.setItem('user', JSON.stringify(data.user || { name: this.form.username }))
          
          // Redirect to dashboard
          this.$router.push('/dashboard')
        } else {
          // Handle specific errors
          if (response.status === 409) {
            if (data.error.includes('username')) {
              this.errors.username = 'Username already exists'
            } else if (data.error.includes('password')) {
              this.generalError = 'Invalid username or password'
            }
          } else {
            this.generalError = data.error || 'Registration failed. Please try again.'
          }
        }
      } catch (error) {
        console.error('Registration error:', error)
        this.generalError = 'Network error. Please check your connection and try again.'
      } finally {
        this.loading = false
      }
    }
  }
}
</script>

<style scoped>
.signup-container {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  padding: 20px;
}

.signup-card {
  background: white;
  padding: 2.5rem;
  border-radius: 12px;
  box-shadow: 0 10px 25px rgba(0, 0, 0, 0.1);
  width: 100%;
  max-width: 400px;
}

.signup-header {
  text-align: center;
  margin-bottom: 2rem;
}

.signup-header h1 {
  color: #333;
  font-size: 2rem;
  font-weight: bold;
  margin-bottom: 0.5rem;
}

.signup-header h2 {
  color: #666;
  font-size: 1.25rem;
  font-weight: normal;
  margin: 0;
}

.signup-form {
  margin-bottom: 1.5rem;
}

.form-group {
  margin-bottom: 1.5rem;
}

.form-group label {
  display: block;
  margin-bottom: 0.5rem;
  color: #333;
  font-weight: 500;
}

.form-group input {
  width: 100%;
  padding: 0.75rem;
  border: 2px solid #e1e5e9;
  border-radius: 6px;
  font-size: 1rem;
  transition: border-color 0.3s ease;
  box-sizing: border-box;
}

.form-group input:focus {
  outline: none;
  border-color: #667eea;
}

.form-group input.error-input {
  border-color: #e74c3c;
}

.error-message {
  color: #e74c3c;
  font-size: 0.875rem;
  margin-top: 0.25rem;
  display: block;
}

.signup-button {
  width: 100%;
  padding: 0.75rem;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border: none;
  border-radius: 6px;
  font-size: 1rem;
  font-weight: 600;
  cursor: pointer;
  transition: opacity 0.3s ease;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.signup-button:hover:not(:disabled) {
  opacity: 0.9;
}

.signup-button:disabled {
  opacity: 0.7;
  cursor: not-allowed;
}

.signup-button.loading {
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

.signin-link {
  text-align: center;
  color: #666;
}

.signin-link a {
  color: #667eea;
  text-decoration: none;
  font-weight: 500;
}

.signin-link a:hover {
  text-decoration: underline;
}

/* Responsive design */
@media (max-width: 480px) {
  .signup-card {
    padding: 1.5rem;
    margin: 1rem;
  }
  
  .signup-header h1 {
    font-size: 1.75rem;
  }
  
  .signup-header h2 {
    font-size: 1.1rem;
  }
}
</style>