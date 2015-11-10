import os
import sys
import glob
import PhotoScan

doc = PhotoScan.app.document

# Maps the mesh path to respective chunk
mesh_dict = {}
# Maps the texture path to respective chunk
texture_dict = {}

# Select the folder that contains two other folders -- 1. photos with no projection and 2. photos with projection
def selectFolder():
	# Select folder with photos
	print ("Selecting folder")

	# User should select a folder containing at least a pair of folders ending with _2 (projection) and _1 (texture)
	path_folder = PhotoScan.app.getExistingDirectory("Specify folder with input photos:")

	# Get the name of each folder inside selected folder
	subdirectories = os.listdir(path_folder)

	# For each folder within the selected folder
	for sub_path in subdirectories:
		# Find the path of the subfolder
		new_path = path_folder + "\\" + sub_path + "\\"

		# Projection folder ends with _2
		if (sub_path.endswith('_2')):
			print("Processing photos on " + new_path)
			# No assigned chunk yet
			mesh_dict[new_path] = None
			# Processes photos (aligns photos and builds dense cloud)
			processPhotos(new_path)

		# Texture folder ends with _1
		elif (sub_path.endswith('_1')):
			print("Adding texture chunk on " + new_path)
			texture_dict[new_path] = None
			# Assigns chunk to this path and adds photos to chunk
			addTextureChunk(new_path)
		
	# Checking save filename
	print("Selecting save filename")
	project_path = PhotoScan.app.getSaveFileName("Specify project filename for saving:")
	if not project_path:
		print("Script aborted")
		return 0

	if project_path[-4:].lower() != ".psz":
		project_path += ".psz"

# Add the texture chunk and the texture photos to the chunk
def addTextureChunk(new_path):
	# Add a chunk and label it with the path name
	chunk = doc.addChunk()
	chunk.label = new_path

	# Adds the texture chunk to the texture path
	texture_dict[new_path] = chunk

	# Add photos
	print("Adding photos for texture chunk")

	# Open a file
	os.chdir(new_path)

	# Add each photo to list
	image_list = []
	for file in glob.glob("*.jpg"):
		print("Adding " + file)
		image_list.append(file)

	# Add photos
	chunk.addPhotos(image_list)

	PhotoScan.app.update()

# Adds photos and builds dense cloud for mesh photos
def processPhotos(new_path):
	print("Script started")

	# Add a chunk
	print("In processing photos: chunk's label is " + new_path)
	chunk = doc.addChunk()
	chunk.label = new_path

	# Adds the projection chunk to the projection path
	mesh_dict[new_path] = chunk

	# Adding photos
	print("Adding photos")

	# Open a file
	os.chdir(new_path)

	# Add each photo to list
	image_list = []
	for file in glob.glob("*.jpg"):
		print("Adding " + file)
		image_list.append(file)

	# Add photos
	chunk.addPhotos(image_list)

	PhotoScan.app.update()
	
	# Align photos
	print("Matching photos")
	chunk.matchPhotos(accuracy=PhotoScan.MediumAccuracy, preselection=PhotoScan.GenericPreselection)

	print("Aligning cameras")
	chunk.alignCameras()

	# Build dense cloud
	print("Building dense cloud")
	chunk.buildDenseCloud(quality=PhotoScan.MediumQuality)

	PhotoScan.app.update()

# After the user has cleaned up their dense cloud (if desired)
def createModel():
	# Build the mesh
	buildMesh()
	# Export cameras to mesh folder
	exportCameras()
	# Export model to mesh folder
	exportModel()
	# Import cameras from mesh to texture folder
	importCameras()
	# Import model from mesh to texture folder
	importModel()
	# Build the texture in the texture chunk
	buildTexture()

	# Save
	print("Saving project path")
	doc.save(project_path)
	
	PhotoScan.app.update()
	print("Script finished")

# Build mesh
def buildMesh():
	# Build model
	print("Building model")

	# Each mesh chunk will build its path's mesh
	for key in mesh_dict:
		mesh_dict[key].buildModel(surface=PhotoScan.Arbitrary, interpolation=PhotoScan.EnabledInterpolation)

	PhotoScan.app.update()

# Exports camera to mesh folder
def exportCameras():
	# Export Cameras
	print("Exporting cameras")

	for key in mesh_dict:
		camera_path = key + "cameras.xml"
		mesh_dict[key].exportCameras(camera_path, format='xml')

	PhotoScan.app.update()

# Exports model to mesh folder
def exportModel():
	print("Exporting model")

	for key in mesh_dict:
		model_path = key + "model.obj"
		mesh_dict[key].exportModel(model_path, format='obj')

	PhotoScan.app.update()

# Imports model from mesh folder to texture chunk
def importCameras():
	print("Importing cameras")

	# For every mesh file
	for key in mesh_dict:
		# Find the corresponding texture file
		corrTextureFile = key[:-2] + "1\\"
		print("Searching for " + corrTextureFile)
		# For every texture file
		for texture_key in texture_dict:
			# If matches with its mesh file
			if corrTextureFile == texture_key:
				print("Found match!")

				# Import camera path (in mesh file path)
				import_cameras_path = key + "cameras.xml"

				# Texture chunk imports camera from mesh file path
				texture_dict[texture_key].importCameras(import_cameras_path, format='xml')
				print("Imported successfully!")

	PhotoScan.app.update()

# Imports model from mesh folder to texture chunk
def importModel():
	print("Importing model")

	# For every mesh file
	for key in mesh_dict:
		# Find the corresponding texture file
		corrTextureFile = key[:-2] + "1\\"

		# For every texture file
		for texture_key in texture_dict:
			# If matches with its mesh file
			if corrTextureFile == texture_key:
				print("Found match")

				# Import model path (in mesh file path)
				import_model_path = key + "model.obj"

				# Texture chunk imports model from mesh file path
				texture_dict[texture_key].importModel(import_model_path, format='obj')
				print("Imported successfully!")

	PhotoScan.app.update()

# Build texture in texture chunk
def buildTexture():
	# Build texture
	print("Building texture")
	for texture_key in texture_dict:
		print("Building texture for " + texture_key)

		texture_dict[texture_key].buildUV(mapping=PhotoScan.GenericMapping)
		texture_dict[texture_key].buildTexture(blending=PhotoScan.MosaicBlending, size=4096)

	print("Successfully built texture!")
	doc.save()

# Print each chunk name in the respective dictionaries (mesh and texture)
def testChunks():
	print("IN MESH:")
	for key in mesh_dict:
		print(mesh_dict[key].label)
	print("IN TEXTURE:")
	for key in texture_dict:
		print(texture_dict[key].label)
	
#User will have two options
PhotoScan.app.addMenuItem("Custom menu/Select folder", selectFolder)
PhotoScan.app.addMenuItem("Custom menu/Create Model", createModel)


