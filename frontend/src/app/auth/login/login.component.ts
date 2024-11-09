import { ChangeDetectorRef, Component, OnInit } from '@angular/core';
import {
  FormBuilder,
  FormGroup,
  Validators,
  AbstractControl,
} from '@angular/forms';
import { AuthService } from '../../../services/auth.service';
import { MatSnackBar } from '@angular/material/snack-bar';  // Import MatSnackBar
import { Router } from '@angular/router';  // Import Router

@Component({
  selector: 'app-login',
  templateUrl: './login.component.html',
  styleUrls: ['./login.component.scss'],
})
export class LoginComponent implements OnInit {
  loginForm!: FormGroup;
  registerForm!: FormGroup;
  isLogin: boolean = true;
  selectedTabIndex: number = 0;

  constructor(
    private fb: FormBuilder,
    private cdr: ChangeDetectorRef,
    private authService: AuthService,
    private snackBar: MatSnackBar,
    private router: Router
  ) {}

  ngOnInit() {
    // get username from local storage if there is one
    // define username string or null
    var username: string | null = null;

    if (typeof window !== 'undefined' && localStorage) {
      username = localStorage.getItem('username');
    }
    

    // Initialize login and register forms
    this.loginForm = this.fb.group({
      username: [username || "", [Validators.required]],
      password: ['', [Validators.required]],
    });

    this.registerForm = this.fb.group({
      username: ['', [Validators.required]],
      full_name: ['', [Validators.required]],
      email: ['', [Validators.required, Validators.email]],
      phone_number: ['', []],  // Phone number is no longer required
      password: ['', [Validators.required]],
      // confirmPassword: ['', [Validators.required]],
    });
  }

  ngAfterViewInit() {
    this.cdr.detectChanges(); // Ensure change detection runs after the view is initialized
  }

  onTabChange(event: any) {
    console.log('Selected Tab Index:', event.index);
  }

  toggleLogin(isLogin: boolean) {
    this.isLogin = isLogin;
    console.log('isLogin:', this.isLogin);
    console.log('selectedTabIndex:', this.selectedTabIndex);

    if (this.isLogin) {
      // Clear confirmPassword validators when switching to login form
      this.registerForm.get('confirmPassword')?.clearValidators();
      this.registerForm.get('confirmPassword')?.updateValueAndValidity();
      this.selectedTabIndex = 0; 
    } else {
      // Set confirmPassword validators when switching to registration form
      this.registerForm
        .get('confirmPassword')
        ?.setValidators([Validators.required, this.passwordMatchValidator]);
      this.registerForm.get('confirmPassword')?.updateValueAndValidity();
      this.selectedTabIndex = 1; 
    }
  }

  passwordMatchValidator(control: AbstractControl) {
    // Ensure the password form control is available before comparing
    const password = this.registerForm?.get('password')?.value;
    const confirmPassword = control.value;

    return password === confirmPassword ? null : { passwordMismatch: true };
  }

  onSubmitLogin() {
    if (this.loginForm.valid) {
      // Assume the login process is successful
      const { username, password } = this.loginForm.value;

      this.authService.login({username, password}).subscribe({
        next: (response: any) => {
          console.log('Login successful:', response);

          // Show a success message using MatSnackBar
          this.snackBar.open('Login Successful!', 'Close', {
            duration: 3000,
            panelClass: ['success-snackbar'],
          });

          this.router.navigate(['/home']);
        },
        error: (err: any) => {
          console.error('Login failed:', err);

          // Show an error message using MatSnackBar
          this.snackBar.open('Login failed. Please try again.', 'Close', {
            duration: 3000,
            panelClass: ['error-snackbar'],
          });
        },
      });

      //navigate to home
      // console.log('navigate to home');
      // setTimeout(() => {
      //   this.router.navigate(['/home']);
      // }, 0);
    }
  }

  onSubmitRegister() {
    if (this.registerForm.valid) {
      const payload = this.registerForm.value;
      this.authService.register(payload).subscribe({
        next: (response: any) => {
          console.log('Registration successful:', response);
  
          // Show success alert
          this.snackBar.open('Registration successful. Please login.', 'Close', {
            duration: 3000,
            panelClass: ['success-snackbar'],
          });

          // set username to local storage
          if (typeof window !== 'undefined' && localStorage) {
            localStorage.setItem('username', payload.username);
          }

          // Refresh the page after successful registration
          window.location.reload();
        },
        error: (err: any) => {
          console.error('Registration failed:', err);
  
          // Show error alert
          this.snackBar.open('Registration failed. Please try again.', 'Close', {
            duration: 3000,
            panelClass: ['error-snackbar'],
          });
        },
      });
    }
  }
  
  
}
