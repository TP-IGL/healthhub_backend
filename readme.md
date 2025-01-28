<p align="center">
  <img src="https://res.cloudinary.com/djn5zzqou/image/upload/v1738100240/TP-IGL/HealthHubLogo.png" width="190" alt="Health Hub Logo" />
  <img />
    <img src="https://skillicons.dev/icons?i=django" height="100" alt="django logo"  />
</p>


# 🏥 Health-Hub

**Health-Hub** is a web application designed to revolutionize patient care by centralizing all medical information in a secure digital format. From medical history to examination results and prescriptions, Health Hub ensures seamless communication between healthcare professionals, enhances care management, and improves the continuity of patient care.

## Features

### Patient Record Management
- 🧾 Centralize all patient information (medical history, treatments, test results, and prescriptions) in a digital file.

### Quick Record Access
- 🔍 Retrieve medical records via NSS or QR code for faster consultations.

### Medical Documentation
- 🩺 Enable doctors to document diagnoses, prescribe medications, and request complementary tests (e.g., biological or radiological exams).

### Consultation Summaries
- 📋 Automatically save consultation summaries, including new diagnoses and patient medical history, for future reference.

### Nursing Care Documentation
- 🩹 Nurses can record details about administered medications, nursing care, and patient observations.

### Pharmacy Integration
- 💊 Support communication with the hospital pharmacy system (SGPH) via REST API for prescription validation and treatment traceability.

### Laboratory and Radiology Reporting
- 🩻 Allow radiologists to upload test results, generate trend graphs (e.g., for glucose or blood pressure), and store diagnostic images securely.


## Getting Started

Follow these steps to set up and run the AGRISISTANCE project locally:

### Prerequisites

Before you begin, ensure you have the following installed:

- [Python](https://www.python.org/): This project requires Python to run. Download and install it from [python.org](https://www.python.org/).
- [Git](https://git-scm.com/): You’ll need Git to clone the repository. Download and install it from [git-scm.com](https://git-scm.com/).



## Cloning the Repository

1. **Clone the repository**: Open your terminal or command prompt and run the following command:

    ```bash
    git clone https://github.com/TP-IGL/healthhub_backend.git
    ```

2. **Navigate to the project directory**:

    ```bash
    cd healthhub_backend
    ```



## Installing Dependencies

To install the required dependencies, run the following command:

```bash
pip install -r requirements.txt
```


## Setting Up Environment Variables

1. **Create a `.env` file** in the `./backend/backend` directory with the following structure:

    ```plaintext
    DATABASE_NAME=igl_db
    DATABASE_USER=root
    DATABASE_PASSWORD=root
    DATABASE_HOST=localhost
    DATABASE_PORT=3306

    CLOUDINARY_CLOUD_NAME = "" 
    CLOUDINARY_API_KEY = "" 
    CLOUDINARY_API_SECRET = "" 
    ```


2. **Explanation of Environment Variables**:
`DATABASE_NAME`
    `DATABASE_USER`, `DATABASE_PASSWORD`, `DATABASE_HOST`,  `DATABASE_PORT` : Configuration for MySQL databases.
 
 - `CLOUDINARY_CLOUD_NAME`, `CLOUDINARY_API_KEY`, `CLOUDINARY_API_SECRET`: Obtain these from [Cloudinary](https://cloudinary.com/). You should create this folder sturcture inside of you media explorer in Cloudinary `TP-IGL/Resultat-Radiologie/`

## Database initializations
Install MySQL from the official [website](https://dev.mysql.com/downloads/installer/).

Run **migrations** to initialize the database with the following command:

```bash
python manage.py migrate
```

Your project should now be running at `http://127.0.0.1:8000`.



## API Documentation

   After running the server, you can use the Swagger integrated documentation to test the available endpoints. The Swagger documentation provides a detailed overview of all the requests you can make to interact with the API.

   - You can find the Swagger documentation for this project at `http://127.0.0.1:8000/swagger/`

   Make sure the server is running at `http://127.0.0.1:8000` before testing the endpoints.


## Contact

For inquiries or feedback, reach out to us at:

- 📧 Email: [ma_fellahi@esi.dz](mailto:ma_fellahi@esi.dz), [mm_oucherif@esi.dz](mailto:mm_oucherif@esi.dz)
- 🌐 WhatsApp: +213 551 61 19 83, +213 660 03 04 03
- **GitHub :** [flh-raouf](https://github.com/flh-raouf) , [Mo-Ouail-Ocf](https://github.com/Mo-Ouail-Ocf)


## License

This project is licensed under the Apache 2.0 License. See the [LICENSE](./LICENSE) file for more information.


