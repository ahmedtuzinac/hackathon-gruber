import { Component, OnInit, inject, ViewChild, ElementRef, HostListener } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { AuthService } from '../../services/auth.service';
import { DatePipe } from '@angular/common';
import { CityLocation } from '../../services/auth.service';
import { DispatchResponse, DispatchPayload } from '../../services/auth.service';
import { MatSidenav } from '@angular/material/sidenav';

export interface SubmissionData {
  loading_location: string;
  loading_date: string | undefined;
  loading_time: string;
  unloading_location: string;
  unloading_date: string | undefined;
  unloading_time: string;
  price: number;
}

interface Message {
  id: number;              // Unique ID for each message
  sender: 'user' | 'bot';  // To differentiate between user and bot messages
  text: string;            // The message content
  timestamp?: Date;        // Optionally add a timestamp
}

@Component({
  selector: 'app-home',
  templateUrl: './home.component.html',
  styleUrls: ['./home.component.scss']
})
export class HomeComponent implements OnInit {
  service = inject(AuthService);

  @ViewChild('sidenav') sidenav!: MatSidenav;
  @ViewChild('chatContainer') private chatContainer!: ElementRef;

  languages = [
    { code: 'en', name: 'English' },
    { code: 'de', name: 'German' },
    { code: 'it', name: 'Italian' }
  ];

  selectedLanguage!: string;
  isMobile: boolean = window.innerWidth < 768;

  loadingLocations: any[] = [];
  unloadingLocations: any[] = [];
  filteredLoadingLocations: any[] = [];
  filteredUnloadingLocations: any[] = [];

  selectedLoadingLocation!: string;
  selectedLoadingDate!: string | undefined;
  selectedLoadingTime!: string;

  selectedUnloadingLocation!: string;
  selectedUnloadingDate!: string | undefined;
  selectedUnloadingTime!: string;

  selectedPrice!: number;  // Price is now a number
  deliveryTimes: string[] = this.generateDeliveryTimes();

  isChatStarted = false;
  isLoading = false;

  userMessage: string = '';
  messages: Message[] = [];
  messageId: number = 0;

  typingIndicator = false;

  public chatbotMessage = 'Hi, I\'m your virtual assistant. How can I help you today?';
  public terminalMessage = 'This message is the initial greeting from the chatbot. It is asking the user for further instructions.';
  public displayedChatbotMessage = '';
  public displayedTerminalMessage = '';

  dispatchResponse!: DispatchResponse;

  constructor(private http: HttpClient, private datePipe: DatePipe) {}

  ngOnInit(): void {
    this.updateIsMobile();

    const savedLanguage = localStorage.getItem('selectedLanguage');
    if (savedLanguage) {
      this.selectedLanguage = savedLanguage;
    } else {
      this.selectedLanguage = 'en';
    }

    // Fetch locations when the component initializes
    this.getAvailableCities().subscribe(locations => {
      this.loadingLocations = locations;
      this.unloadingLocations = locations;
    });

    // this.startTypingEffect(this.chatbotMessage, 'chatbot');
    // this.startTypingEffect(this.terminalMessage, 'terminal');
  }

  ngAfterViewChecked() {
    this.scrollToBottom();
  }

  @HostListener('window:resize', ['$event'])
  onResize(event: Event): void {
    this.updateIsMobile();
  }

  private updateIsMobile(): void {
    this.isMobile = window.innerWidth < 768; // Set your mobile breakpoint here
  }

  scrollToBottom(): void {
    try {
      this.chatContainer.nativeElement.scrollTop = this.chatContainer.nativeElement.scrollHeight;
    } catch (err) {
      console.error('Scroll to bottom failed:', err);
    }
  }

  // Submit Handler
  // Function to simulate typing effect
  startTypingEffect(message: string, target: 'chatbot' | 'terminal') {
    const targetMessage = target === 'chatbot' ? 'displayedChatbotMessage' : 'displayedTerminalMessage';
    let i = 0;
    const interval = setInterval(() => {
      // Update message progressively
      if (i < message.length) {
        this[targetMessage] += message.charAt(i);
        i++;
      } else {
        clearInterval(interval); // Stop when message is fully displayed
      }
    }, 10); // Adjust typing speed (in ms)
  }

  // Submit Handler
  onSubmit(): void {
    // Set loading state to true
    this.isLoading = true;
  
    const formattedLoadingDate = this.formatDateToYYMMDD(this.selectedLoadingDate);
    const formattedUnloadingDate = this.formatDateToYYMMDD(this.selectedUnloadingDate);
  
    const submissionData = this.prepareDataForSubmission();
  
    // Update the submission data with the formatted date
    submissionData.loading_date = formattedLoadingDate;
    submissionData.unloading_date = formattedUnloadingDate;
  
    console.log(submissionData); // Send this data to the backend API
  
    // Find the country for loading and unloading locations
    const loadingLocation = this.loadingLocations.find(location => location.city === this.selectedLoadingLocation);
    const unloadingLocation = this.unloadingLocations.find(location => location.city === this.selectedUnloadingLocation);
  
    // If locations are found, extract their countries
    const loadCountry = loadingLocation ? loadingLocation.country : 'Unknown';
    const unloadCountry = unloadingLocation ? unloadingLocation.country : 'Unknown';
  
    const dispatchPayload: DispatchPayload = {
      load_address: {
        city: this.selectedLoadingLocation,
        country: loadCountry // Country for the loading location
      },
      unload_address: {
        city: this.selectedUnloadingLocation,
        country: unloadCountry // Country for the unloading location
      },
      price: this.selectedPrice
    };
  
    // Call the dispatch API
    this.service.dispatch(dispatchPayload).subscribe({
      next: (response: DispatchResponse) => {
        this.dispatchResponse = response; // Save the response
        this.isChatStarted = true;
        console.log('Dispatch successful:', response);
  
        // Set the response data for chatbot and terminal messages
        const chatbotMessage = this.dispatchResponse.direct_message;
        const terminalMessage = this.dispatchResponse.reason_why_you_choose_this_partner;
  
        // Start typing effect for chatbot and terminal messages
        this.startTypingEffect(chatbotMessage, 'chatbot');
        this.startTypingEffect(terminalMessage, 'terminal');
  
        // Set loading state to false once response is received
        this.isLoading = false;
      },
      error: (error) => {
        console.error('Dispatch error:', error);
        // Set loading state to false if an error occurs
        this.isLoading = false;
      }
    });
  }
  
  
  
  isFormValid(): boolean {
    return (
      this.selectedLoadingLocation &&
      this.selectedLoadingDate &&
      this.selectedLoadingTime &&
      this.selectedUnloadingLocation &&
      this.selectedUnloadingDate &&
      this.selectedUnloadingTime &&
      this.selectedPrice
    ) ? true : false;
  }
  
  // startTypingEffect(message: string, target: 'chatbot' | 'terminal') {
  //   let currentIndex = 0;
  //   const interval = setInterval(() => {
  //     if (currentIndex < message.length) {
  //       if (target === 'chatbot') {
  //         this.displayedChatbotMessage += message[currentIndex];
  //       } else if (target === 'terminal') {
  //         this.displayedTerminalMessage += message[currentIndex];
  //       }
  //       currentIndex++;
  //     } else {
  //       clearInterval(interval);
  //     }
  //   }, 50); // Adjust typing speed by changing the interval time
  // }

  // Prepare data for submission
  prepareDataForSubmission(): SubmissionData {
    return {
      loading_location: this.selectedLoadingLocation,
      loading_date: this.selectedLoadingDate,
      loading_time: this.selectedLoadingTime,
      unloading_location: this.selectedUnloadingLocation,
      unloading_date: this.selectedUnloadingDate,
      unloading_time: this.selectedUnloadingTime,
      price: this.selectedPrice
    };
  }

  formatDateToYYMMDD(date: string | undefined): string | undefined {
    if (date) {
      const formattedDate = this.datePipe.transform(date, 'YYYY-MM-dd');
      return formattedDate !== null ? formattedDate : undefined; // Ensure the result is not null
    }
    return undefined; // Return undefined if date is falsy
  }
  

  // Language change handler
  getAvailableCities(): Observable<CityLocation[]> {
    return this.service.getAvailableCities();
  }

  generateDeliveryTimes(): string[] {
    const times: string[] = [];
    for (let hour = 0; hour < 24; hour++) {
      for (let min = 0; min < 60; min += 30) {
        times.push(
          `${hour.toString().padStart(2, '0')}:${min.toString().padStart(2, '0')}`
        );
      }
    }
    return times;
  }

  filterLocations(event: Event, type: 'loading' | 'unloading'): void {
    const input = event.target as HTMLInputElement;
    const query = input.value;
    const filteredLocations = (type === 'loading' ? this.loadingLocations : this.unloadingLocations)
      .filter(location => location.city.toLowerCase().includes(query.toLowerCase()));

    if (type === 'loading') {
      this.filteredLoadingLocations = filteredLocations;
    } else {
      this.filteredUnloadingLocations = filteredLocations;
    }
  }

  onLanguageChange(event: any): void {
    const language = event.value;
    localStorage.setItem('selectedLanguage', language); // Save to localStorage
    this.selectedLanguage = language;
    // You can also add logic to update the language throughout your app, e.g., by triggering a translation reload.
  }

  onSendMessage(): void {
    if (this.userMessage.trim()) {
      const message = this.userMessage;
      const id_conversation = localStorage.getItem('conversationId');
      
      // Increment the message ID for the user message
      const userMessage: Message = {
        id: this.messageId++,  // Increment ID
        sender: 'user',
        text: message
      };
      this.messages.push(userMessage);  // Add user message to the messages array
      this.userMessage = '';  // Clear the input field after sending
  
      this.isLoading = true;  // Show loader while waiting for response
  
      // Send message to the service
      this.service.sendMessage(message, id_conversation!).subscribe({
        next: (response) => {
          console.log('Message sent:', response);
          this.isLoading = false;
  
          // Show typing indicator (if applicable)
          this.showTypingIndicator();
  
          // Simulate or process the bot's response
          const botMessage = response.message || 'This is a bot response to: ' + message;  // You can adjust this based on your API response format
          const botMessageObj: Message = {
            id: this.messageId++,  // Increment ID for the bot message
            sender: 'bot',
            text: botMessage
          };
          
          // Add bot message to the messages array
          this.messages.push(botMessageObj);  
        },
        error: (error) => {
          console.error('Error sending message:', error);
          this.isLoading = false;
        }
      });
    } else {
      console.log('Message cannot be empty');
    }
  }
  

  showTypingIndicator(): void {
    this.typingIndicator = true;
  }

  // onStartChat() {
  //   this.isChatStarted = true;
  // }

  isSidenavOpened(): boolean {
    console.log("check sidenav opened", this.sidenav?.opened);
    return this.sidenav?.opened ?? false;
  }
}
