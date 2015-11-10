import os
import sys
import glob
import PhotoScan

doc = PhotoScan.app.document

# Maps the mesh path to respective chunk
mesh_dict = {}
# Maps the texture path to respective chunk
texture_dict = {}

def selectFolder():
	# Select folder with photos
	print ("Selecting folder")

	# User should select a folder containing at least a pair of folders ending with _2 (projection) and _1 (texture)
	path_folder = PhotoScan.app.getExistingDirectory("Specify folder with input photos:")

	subdirectories = os.listdir(path_folder)

	# For each folder within the selected folder
	for sub_path in subdirectories:
		# Find the path of the subfolder
		new_path = path_folder + "\\" + sub_path + "\\"
		print("NEW PATH: " + new_path)
		# Projection folder
		if (sub_path.endswith('_2')):
			print("Processing photos on " + new_path)
			# No assigned chunk yet
			mesh_dict[new_path] = None
			# Processes photos
			processPhotos(new_path)
		# Texture folder
		elif (sub_path.endswith('_1')):
			print("Adding texture chunk on " + new_path)
			texture_dict[new_path] = None
			# Assigns chunk to this path and adds photos
			addTextureChunk(new_path)
		
	# Checking save filename
	print("Selecting save filename")
	project_path = PhotoScan.app.getSaveFileName("Specify project filename for saving:")
	if not project_path:
		print("Script aborted")
		return 0

	if project_path[-4:].lower() != ".psz":
		project_path += ".psz"

# Add the texture chunk and the texture photos
def addTextureChunk(new_path):
	# Add a chunk and label it with the path name
	chunk = doc.addChunk()
	chunk.label = new_path

	# Adds the texture chunk to the texture path
	texture_dict[new_path] = chunk

	# Add photos
	print("Adding photos for texture chunk")
	print("FILE PATH: " + new_path)

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

# Adds photos and builds dense cloud
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
	print("FILE PATH: " + new_path)

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
	print("Aligning photos")
	print("Matching photos")
	chunk.matchPhotos(accuracy=PhotoScan.MediumAccuracy, preselection=PhotoScan.GenericPreselection)
	print("Aligning photos...")
	chunk.alignCameras()

	# Build dense cloud
	print("Building dense cloud")
	chunk.buildDenseCloud(quality=PhotoScan.MediumQuality)

	PhotoScan.app.update()

# Build mesh (after clean up of dense cloud)
def buildMesh():
	# Build model
	print("Building model")

	# Each chunk will build its path's mesh
	for key in mesh_dict:
		mesh_dict[key].buildModel(surface=PhotoScan.Arbitrary, interpolation=PhotoScan.EnabledInterpolation)

	PhotoScan.app.update()

def finishUp():
	print("Finishing up")
	print("In finish...exporting cameras")
	exportCameras()
	print("In finish...exporting model")
	exportModel()
	print("In finish...importing cameras")
	importCameras()
	print("In finish...importing model")
	importModel()
	print("In finish...building texture")
	buildTexture()

	# Save
	print("Saving project path")
	doc.save(project_path)
	
	PhotoScan.app.update()
	print("Script finished")

# Exports camera to mesh folder
def exportCameras():
	# Export Cameras
	print("Exporting cameras")
	for key in mesh_dict:
		camera_path = key + "cameras.xml"
		print("Camera path is " + camera_path)
		mesh_dict[key].exportCameras(camera_path, format='xml')
		print("Exported cameras to " + camera_path)
	PhotoScan.app.update()

# Exports model to mesh folder
def exportModel():
	print("Exporting model")
	for key in mesh_dict:
		model_path = key + "model.obj"
		mesh_dict[key].exportModel(model_path, format='obj')
		print("Exported model to" + model_path)
	PhotoScan.app.update()

# Imports model from texture folder
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
			print("Searching through texture dict...on " + texture_key)
			if corrTextureFile == texture_key:
				print("Found match!")
				# Import camera path (in mesh file path)
				import_cameras_path = key + "cameras.xml"
				# Texture chunk imports camera from mesh file path
				texture_dict[texture_key].importCameras(import_cameras_path, format='xml')
				print("Imported successfully!")
	PhotoScan.app.update()

# Imports model from texture folder
def importModel():
	print("Importing model")
	# For every mesh file
	for key in mesh_dict:
		# Find the corresponding texture file
		corrTextureFile = key[:-2] + "1\\"
		print("Searching for " + corrTextureFile)

		# For every texture file
		for texture_key in texture_dict:
			# If matches with its mesh file
			print("Searching through texture dict...on " + texture_key)
			if corrTextureFile == texture_key:
				print("Found match")
				# Import model path (in mesh file path)
				import_model_path = key + "model.obj"
				# Texture chunk imports model from mesh file path
				texture_dict[texture_key].importModel(import_model_path, format='obj')
				print("Imported successfully!")
	PhotoScan.app.update()

# Build texture
def buildTexture():
	# Build texture
	print("Building texture")
	for texture_key in texture_dict:
		print("Building texture for " + texture_key)

		#these don't work
		#texture_dict[texture_key].buildTexture(blending=PhotoScan.MosaicBlending, size=4096)
		#texture_dict[texture_key].buildTexture(mapping = "adaptive", blending = "mosaic", color_correction = False, size = 4096, count = 1)
				#haven't tested yet		#doc.activeChunk.buildTexture(mapping="generic", blending="average", width=2048, height=2048)		#doesn't work		#texture_dict[texture_key].buildUV(mapping = mapping, count = 1)
		#texture_dict[texture_key].buildTexture(blending = blending , color_correction = color_corr, size = atlas_size)

		texture_dict[texture_key].buildUV(mapping=PhotoScan.GenericMapping)
		texture_dict[texture_key].buildTexture(blending=PhotoScan.MosaicBlending, size=4096)

	print("Successfully built texture!")
	doc.save()

#Print each chunk name in the respective dictionaries (mesh and texture)
def testChunks():
	print("IN MESH:")
	for key in mesh_dict:
		print(mesh_dict[key].label)
	print("IN TEXTURE:")
	for key in texture_dict:
		print(texture_dict[key].label)
	
PhotoScan.app.addMenuItem("Custom menu/Select folder", selectFolder)
PhotoScan.app.addMenuItem("Custom menu/Test chunks", testChunks)
PhotoScan.app.addMenuItem("Custom menu/Build mesh", buildMesh)
PhotoScan.app.addMenuItem("Custom menu/Finish up", finishUp)


