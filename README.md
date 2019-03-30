# Spiderweb-Generator
Our  objective is to design and implement a cobweb generation tool that allows a user to create and customize cobwebs between two selected objects


Planned Features Include:

User Interface: User is able to manipulate various attributes related to the generation of the cobwebs to allow for absolute customization control. 

Object Selection: User is able to select which objects in the scene the cobwebs will apply to. 

Start/End Point Selection: Determines appropriate positions to begin and end the curve for a cobweb string. 

Curve Verification: Should allow for curves that will pass through geometry from start to end point to be disregarded before web generation.

Web Density: Determine the number of strings per vertex to create. 

Amount of Hang: Determines how much the string will be affected by gravity. This informs the length and number of segments each created curve will have. 

Web Intricacy (levels of application): Determines how many additional levels of strings to apply to the cobweb. For example, level 1 creates base strings connecting from object 1 to object 2, level 2 creates strings connecting between the level 1 strings (a curve to another curve). See figure 4.2.3 in section 4.0 Design Sketches.  

Randomization of Attributes: Allows the user to determine an amount of variance to each of the properties that can be defined in the user interface: density, and amount of hang. 

Generate Geometry from Curve Data: Create polygon geometry of strings with predetermined radius from curve data. (could be done with implicit or explicit modelling TBD)

Manipulate Curve Around Geometry: Should allow for curves that are not verified (intersects with geometry) to reposition their control points along the surface of the reference objects.

