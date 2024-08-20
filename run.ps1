# Determine the current directory
$CurrentDir = Get-Location

# Run the Docker container with a bind mount for the source code (including the database) and GPU support
docker run -it --rm `
  --gpus all `
  -v "${CurrentDir}:/root" `
  -p 8080:8080 `
  -w /root viewfarm_v2
