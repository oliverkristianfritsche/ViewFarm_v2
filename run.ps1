# Determine the current directory
$CurrentDir = Get-Location

# Run the Docker container with a bind mount for the source code (including the database) and GPU support
docker run -it --rm `
  --gpus all `
  --network host `
  -v "${CurrentDir}:/root" `
  -v "G:/My Drive/repurposeio:/root/reprocessio" `
  -w /root viewfarm_v2
