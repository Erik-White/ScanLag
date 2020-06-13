from typing import Any, Tuple, List
from abc import ABC, abstractmethod
from numpy import ndarray
from skimage.transform._geometric import GeometricTransform, SimilarityTransform


class AlignTransform(ABC):
    """
    An abstract class to provide image alignment
    """
    def __init__(self, image_ref: ndarray, transform_model: GeometricTransform):
        """
        Initialise a new instance of the AlignTransform

        :param image_ref: a reference image to align with
        :param transform_model: a GeometricTransform type used when warping images to match image_ref
        """
        self.image_ref = image_ref
        self.transform_model = transform_model

    @property
    @abstractmethod
    def image_ref(self) -> Any:
        """
        Store the reference image as its descriptors, or similar
        """
        raise NotImplementedError("This property must be implemented in a derived class")

    @image_ref.setter
    @abstractmethod
    def image_ref(self, val: ndarray):
        """
        Store the reference image as its descriptors, or similar
        """
        raise NotImplementedError("This property must be implemented in a derived class")

    @property
    def transform_model(self) -> GeometricTransform:
        return self._transform_model

    @transform_model.setter
    def transform_model(self, val: GeometricTransform):
        self._transform_model = val

    @abstractmethod
    def align(self, image: ndarray, precise: bool = True, **kwargs) -> ndarray:
        """
        Align an image with the current reference image

        :param image: an image to align
        :param precise: peform a second alignment pass, more accurate but much slower
        :param kwargs: keyword arguments
        :returns: an image aligned with image_ref
        """
        raise NotImplementedError("This property must be implemented in a derived class")

    @abstractmethod
    def align_transform(self, image: ndarray, **kwargs) -> GeometricTransform:
        """
        Calculate the transformation needed to align the image with the current reference image

        :param image: an image to align
        :param kwargs: keyword arguments
        :returns: a transformation that will align the image with image_ref
        """
        raise NotImplementedError("This property must be implemented in a derived class")


class DescriptorAlignTransform(AlignTransform):
    """
    Image alignment using a DescriptorExtractor
    """
    from skimage.feature import ORB
    from skimage.feature.util import DescriptorExtractor

    def __init__(
        self,
        image_ref: ndarray,
        transform_model: GeometricTransform = SimilarityTransform,
        descriptor_extractor_model: DescriptorExtractor = ORB,
        **kwargs
    ):
        """
        Initialise a new instance of the DescriptorAlignTransform

        The reference image is stored as its descriptors and keypoints as extracted by descriptor_extractor_model

        :param image_ref: a reference image to align with
        :param transform_model: a GeometricTransform type used when warping images to match image_ref
        :param descriptor_extractor_model: a DescriptorExtractor and FeatureDectector type used for image feature extraction
        :param kwargs: keyword arguments used when initialising descriptor_extractor_model
        """
        self.descriptor_extractor = descriptor_extractor_model(**kwargs)
        super().__init__(image_ref, transform_model)

    @property
    def descriptor_extractor(self) -> DescriptorExtractor:
        return self._descriptor_extractor

    @descriptor_extractor.setter
    def descriptor_extractor(self, val: DescriptorExtractor):
        self._descriptor_extractor = val

    @property
    def image_ref(self) -> Tuple[List, List]:
        """
        The reference image as its descriptors and keypoints
        """
        return self._image_ref_descriptors, self._image_ref_keypoints

    @image_ref.setter
    def image_ref(self, val: ndarray):
        """
        Store the reference image as its descriptors and keypoints
        """
        self._image_ref_descriptors, self._image_ref_keypoints = self._extract_keypoints(val)

    def align(self, image: ndarray, precise: bool = True, **kwargs) -> ndarray:
        """
        Align an image with the current reference image

        :param image: an image to align
        :param precise: peform a second alignment pass, more accurate but much slower
        :param kwargs: keyword arguments passed to skimage.feature.match_descriptors
        :returns: an image aligned with image_ref
        """
        from warnings import warn
        from skimage.transform import warp

        # Calulcate the transformation
        transform = self.align_transform(image, **kwargs)

        if precise:
            try:
                # Perform second pass to get a very accurate alignment
                image_aligned = warp(image.copy(), transform.inverse, order = 1, preserve_range = False)
                transform += self.align_transform(image_aligned, **kwargs)
            except RuntimeError:
                warn("Unable to perform second pass image alignment, no keypoints could be found.", RuntimeWarning)

        # Adjust the image using the calculated transform
        return warp(image, transform.inverse, order = 3, preserve_range = True)

    def align_transform(self, image: ndarray, **kwargs) -> GeometricTransform:
        """
        Calculate the transformation needed to align the image with the current reference image

        :param image: an image to align
        :param kwargs: keyword arguments passed to skimage.feature.match_descriptors
        :returns: a transformation that will align the image with image_ref
        """
        from numpy import flip
        from skimage.feature import match_descriptors
        from skimage.measure import ransac

        descriptors_ref, keypoints_ref = self.image_ref
        descriptors, keypoints = self._extract_keypoints(image)

        try:
            # Used matched features to filter keypoints
            matches = match_descriptors(descriptors_ref, descriptors, cross_check = True, **kwargs)
            matches_ref, matches = keypoints_ref[matches[:, 0]], keypoints[matches[:, 1]]

            # Robustly estimate transform model with RANSAC
            transform_robust, inliers = ransac(
                (matches_ref, matches),
                self.transform_model,
                min_samples = 8,
                residual_threshold = 0.8,
                max_trials = 1000
            )
        except (RuntimeError, IndexError) as err:
            raise RuntimeError(err, "No feature matches could be found between the two images")

        # The translation needs to be inverted
        return (self.transform_model(rotation = transform_robust.rotation)
                + self.transform_model(translation = -flip(transform_robust.translation)))

    def _extract_keypoints(self, image: ndarray) -> Tuple[ndarray, ndarray]:
        """
        Detect and extract descriptors and keypoints from an image

        :param image: the image to extract descriptors and keypoints
        :returns: a tuple of descriptor and keypoints
        """
        from numpy import asarray
        from skimage.color import rgb2gray
        from .imaging import image_as_rgb

        # ORB can only handle 2D arrays
        if len(image.shape) > 2:
            image = rgb2gray(image_as_rgb(image))

        try:
            self.descriptor_extractor.detect_and_extract(image)
        except AttributeError:
            self.descriptor_extractor.detect(image)
            self.descriptor_extractor.extract(self.descriptor_extractor.keypoints)

        return asarray(self.descriptor_extractor.descriptors), asarray(self.descriptor_extractor.keypoints)