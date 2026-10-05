import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { HttpClient } from '@angular/common/http';
@Component({
  selector: 'app-root',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './app.html',
  styleUrl: './app.css'
})
export class AppComponent {
  selectedSection: string = '';
  selectedFile: File | null = null;
  previewUrl: string | null = null;
  result: any = null;

  soilType: string = '';
  rainfall: string = '';
  temperature: string = '';


  openSection(section: string) {
    this.selectedSection = section;
  }
  yieldForm = {
  Area: '',
  Item: '',
  soil_type:'',
  Year: 0,
  average_rain_fall_mm_per_year: 0,
  pesticides_tonnes: 0,
  avg_temp: 0
  
};

yieldResult: any = null;

  onFileSelected(event: any) {
    this.selectedFile = event.target.files[0];

    if (this.selectedFile) {
      const reader = new FileReader();
      reader.onload = (e: any) => {
        this.previewUrl = e.target.result;
      };
      reader.readAsDataURL(this.selectedFile);
    }
  }

  // uploadImage() {
  //   if (!this.selectedFile) return;

  //   const formData = new FormData();
  //   formData.append('file', this.selectedFile);

  //   fetch('http://127.0.0.1:8000/predict', {
  //     method: 'POST',
  //     body: formData
  //   })
  //     .then(res => res.json())
  //     .then(data => {
  //       this.result = data;
  //     })
  //     .catch(err => {
  //       console.error(err);
  //     });
  // }


  uploadImage() {
  if (!this.selectedFile) {
    alert('Please select an image first');
    return;
  }

  const formData = new FormData();
  formData.append('file', this.selectedFile);

  this.http.post('http://127.0.0.1:8000/predict', formData)
    .subscribe({
      next: (res: any) => {
        console.log('Disease API success:', res);
        this.result = res;
      },
      error: (err) => {
        console.error('Disease API error:', err);
        alert('Disease prediction failed');
      }
    });
}


constructor(private http: HttpClient) {}

predictYield() {
  this.http.post('http://127.0.0.1:8000/predict-yield', this.yieldForm)
    .subscribe({
      next: (res: any) => {
        this.yieldResult = res;
      },
      error: (err) => {
        console.error('Yield error:', err);
        alert('Yield prediction failed');
      }
    });
}
}