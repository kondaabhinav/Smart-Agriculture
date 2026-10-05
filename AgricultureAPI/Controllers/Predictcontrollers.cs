using Microsoft.AspNetCore.Mvc;
using System.Net.Http.Headers;

namespace AgricultureAPI.Controllers
{
    [ApiController]
    [Route("api/[controller]")]
    public class PredictController : ControllerBase
    {
        [HttpPost("disease")]
        public async Task<IActionResult> PredictDisease(IFormFile file)
        {
            if (file == null || file.Length == 0)
            {
                return BadRequest(new { message = "No file uploaded" });
            }

            using var client = new HttpClient();
            using var content = new MultipartFormDataContent();

            using var stream = file.OpenReadStream();
            var fileContent = new StreamContent(stream);
            fileContent.Headers.ContentType = new MediaTypeHeaderValue(file.ContentType);

            content.Add(fileContent, "file", file.FileName);

            var response = await client.PostAsync("http://127.0.0.1:8000/predict", content);

            if (!response.IsSuccessStatusCode)
            {
                var errorText = await response.Content.ReadAsStringAsync();
                return StatusCode(500, new
                {
                    message = "Python API call failed",
                    details = errorText
                });
            }

            var result = await response.Content.ReadAsStringAsync();
            return Content(result, "application/json");
        }

        [HttpPost("yield")]
        public IActionResult PredictYield([FromBody] YieldRequest request)
        {
            if (string.IsNullOrWhiteSpace(request.SoilType) ||
                string.IsNullOrWhiteSpace(request.Rainfall) ||
                string.IsNullOrWhiteSpace(request.Temperature))
            {
                return BadRequest(new { message = "Please fill all fields" });
            }

            if (!double.TryParse(request.Rainfall, out double rainfall))
            {
                return BadRequest(new { message = "Rainfall must be a number" });
            }

            if (!double.TryParse(request.Temperature, out double temperature))
            {
                return BadRequest(new { message = "Temperature must be a number" });
            }

            double predictedYield;
            string soil = request.SoilType.Trim().ToLower();

            if (soil == "loamy")
            {
                predictedYield = 5.0;
            }
            else if (soil == "clay")
            {
                predictedYield = 4.2;
            }
            else if (soil == "sandy")
            {
                predictedYield = 3.6;
            }
            else
            {
                predictedYield = 3.8;
            }

            predictedYield += rainfall / 1000.0;
            predictedYield -= Math.Abs(temperature - 25) * 0.08;

            if (predictedYield < 1)
            {
                predictedYield = 1;
            }

            return Ok(new
            {
                predictedYield = predictedYield.ToString("0.0") + " tons/hectare"
            });
        }
    }

    public class YieldRequest
    {
        public string SoilType { get; set; } = "";
        public string Rainfall { get; set; } = "";
        public string Temperature { get; set; } = "";
    }
}